import asyncio
import logging
from fastapi import APIRouter, Depends, Query, Request, HTTPException, Response, status
from fastapi.responses import JSONResponse
from bot.api.dependencies import get_container
from bot.infrastructure.database.db_container.container import Container
from bot.infrastructure.database.use_cases.user import admin_user_analytics, admin_chat_with_user
from bot.infrastructure.database.use_cases.broadcast import admin_broadcasts
from bot.infrastructure.database.use_cases.add_song import add_songs
from bot.infrastructure.database.use_cases.promo import create_promocode, get_promocodes
from bot.service.broadcast import run_broadcast, escape_markdown_v2
from bot.utils.enums import UpdateSong
from .schemas import (
    BroadcastMessageIn,
    UsersResponse,
    SongLogsResponse,
    BroadcastsResponse,
    LetSongRequest,
    LetSongResponse,
    TelegramUser,
    SongAudioResponse,
    PromoCodesResponse,
    PromoCodeItem,
    PromoCodeCreateRequest,
)
from bot.infrastructure.database import get_session
from bot.infrastructure.database.db_container import container_factory
from .auth import get_current_telegram_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(get_current_telegram_user)]
)

@router.get(
    "/users",
    response_model=UsersResponse,
)
async def get_admin_users(
    response: Response,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    q: str | None = None,
    db: Container = Depends(get_container),
):
    users = await admin_user_analytics(db, offset, limit, q)
    count_users = len(await db.user_service.user_repo.get_all())
    response.headers["X-Total-Count"] = str(count_users)
    return {
        "users": [
            {
                "id": i,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "count_referrals": user.count_referrals,
                "count_aviable_songs": user.count_aviable_songs,
                "count_generated_songs": user.count_generated_songs,
                "avg_grade": user.avg_grade,
                "created_at": user.created_at
            }
            for i, user in enumerate(users)
        ],
        "total": count_users,
        "offset": offset,
        "limit": limit
    }


@router.get(
    "/promocodes",
    response_model=PromoCodesResponse,
)
async def list_promocodes(
    response: Response,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Container = Depends(get_container),
):
    promo_codes = await get_promocodes(db, offset, limit)
    total = len(await db.promo_code.get_all())
    response.headers["X-Total-Count"] = str(total)
    return {
        "items": [
            PromoCodeItem(
                id=promo.id,
                code=promo.code,
                bonus_songs=promo.bonus_songs,
                valid_until=promo.valid_until,
                is_active=promo.is_active,
                created_at=promo.created_at,
            )
            for promo in promo_codes
        ],
        "total": total,
        "offset": offset,
        "limit": limit,
    }


@router.post(
    "/promocodes",
    response_model=PromoCodeItem,
)
async def create_promocode_endpoint(
    body: PromoCodeCreateRequest,
    db: Container = Depends(get_container),
):
    promo = await create_promocode(
        db,
        code=body.code,
        valid_until=body.valid_until,
        bonus_songs=body.bonus_songs,
        is_active=body.is_active,
    )
    if promo is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Промокод уже существует")

    return PromoCodeItem(
        id=promo.id,
        code=promo.code,
        bonus_songs=promo.bonus_songs,
        valid_until=promo.valid_until,
        is_active=promo.is_active,
        created_at=promo.created_at,
    )


@router.get(
    "/logs",
    response_model=SongLogsResponse,
)
async def get_chat_with_user(
    response: Response,
    telegram_id: int = Query(..., description="Telegram ID пользователя"),
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Container = Depends(get_container),
):
    chat_histoty = await admin_chat_with_user(db, telegram_id, offset, limit)
    all = await db.song_log.get_all(telegram_id=telegram_id)
    response.headers["X-Total-Count"] = str(len(all))

    return {
        "logs": [
            {
                "telegram_id": c.telegram_id,
                "initiator": c.initiator,
                "msg": c.msg,
                "created_at": c.created_at
            }
            for c in chat_histoty
        ],
        "total": len(all),
        "offset": offset,
        "limit": limit
    }


@router.get(
    "/song/{song_id}",
    response_model=SongAudioResponse,
)
async def get_song_file(
    request: Request,
    song_id: str,
    db: Container = Depends(get_container),
):
    song = await db.song_meta.get(song_id)
    if song is None or song.key_s3 is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")

    s3 = request.state.s3
    presigned_url = await s3.get_presigned_url(song.key_s3)

    return SongAudioResponse(id=song.id, title=song.title, url=presigned_url)


@router.post("/broadcast")
async def start_broadcast(
    request: Request,
    payload: BroadcastMessageIn,
    db: Container = Depends(get_container),
):
    print(payload)
    try:
        text = escape_markdown_v2(payload.text)
        broadcast = await db.broadcast.create(text=text)
        await db.session.commit()
        asyncio.create_task(run_broadcast(
            get_session, container_factory, request.state.tg_bot, payload.user_ids, broadcast.id))
        return {"success": True}
    except Exception as e:
        logging.error(f"Broadcast doesnt started: {str(e)}")
        return {"success": False, "detail": str(e)}


@router.get("/broadcasts", response_model=BroadcastsResponse)
async def start_broadcast(
    response: Response,
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=100),
    db: Container = Depends(get_container),
):
    broadcasts = await admin_broadcasts(db, offset, limit)
    all = await db.broadcast.get_all()
    response.headers["X-Total-Count"] = str(len(all))
    return {
        "broadcasts": [
            {
            "id": b.id,
            "text": b.text,
            "is_sent": b.is_sent,
            "count_users": b.count_users,
            "count_success_delivered": b.count_success_delivered,
            "created_at": b.created_at
            }
        for b in broadcasts],
        "total": 25,
        "offset": 0,
        "limit": 10
    }
    
@router.post("/give-song", response_model=LetSongResponse)
async def let_song(
    body: LetSongRequest,
    db: Container = Depends(get_container),
):
    response = await add_songs(db, body.telegram_id, body.count, reason=UpdateSong.BY_ADMIN)
    if not response:
        return LetSongResponse(success=False, detail="error")
    
    return LetSongResponse(success=True)