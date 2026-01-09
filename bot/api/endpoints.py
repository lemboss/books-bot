import logging
import asyncio
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from urllib.parse import quote
from bot.api.service.crypto import generate_pkce_pair
from bot.api.service.requests import vk_exchange_code_to_access, ok_exchange_code_to_access, ok_get_user_id

from bot.infrastructure.database import get_session

from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

templates = Jinja2Templates(directory="bot/api/templates")

@router.get("/vk")
async def auth(
        request: Request,
        telegram_id: int
    ):
    redis = request.state.redis
    code_verifier, code_challenge = generate_pkce_pair()
    await redis.set(telegram_id, code_verifier)    

    return templates.TemplateResponse(
        name='index.html', 
        context={
            "request": request,
            "client_id": settings.vk.client_id,  
            "domain": settings.domain,  
            "callback_uri": settings.vk.redirect_uri,
            "code_challenge": code_challenge,
            "state": telegram_id,
        }
    )

@router.get("/vk_callback")
async def vk_callback(request: Request):
    db_container = request.state.db_container

    try:
        params = dict(request.query_params)
        VkCodeRequest(**params)
    except Exception as e:
        return HTTPException(status_code=422, detail="Страница не найдена")
    redis = request.state.redis
    state = int(params.get("state"))
    if not await redis.exists(state):
        return HTTPException(status_code=422, detail="Страница не найдена")
    user = await db_container.user_service.user_repo.get(state)
    if user is None:
        return RedirectResponse(url="https://t.me/")
    
    code = params.get("code")
    device_id = params.get("device_id")
    redirect_url = settings.domain + settings.vk.redirect_uri
    client_id = settings.vk.client_id
    code_verifier = await redis.get(state)
    try:
        data = await vk_exchange_code_to_access(
            state=state, 
            code=code, 
            device_id=device_id, 
            redirect_url=redirect_url, 
            client_id=client_id, 
            code_verifier=code_verifier
        )
        vk_user_id = data.get("user_id")
        print(vk_user_id)
        logger.info(f"exchange success, tg={state}, vk user id = {vk_user_id}")
    except Exception as e:
        logger.error(f"exchange error, tg={state} vk user id ?")
        return HTTPException(status_code=422)

    db_container = request.state.db_container
    await db_container.user_service.end_register_vk(state, vk_user_id)
    await db_container.session.commit()

    return templates.TemplateResponse(
        "vk_deeplink.html",
        {
            "request": request,
            "channel_id": settings.vk.channel_id
        }
    )

@router.get("/ok")
async def auth(
        request: Request,
        telegram_id: int
    ): 
    return RedirectResponse(
        url=f"https://connect.ok.ru/oauth/authorize?client_id={settings.ok.client_id}&scope=VALUABLE_ACCESS;LONG_ACCESS_TOKEN;GROUP_CONTENT&response_type=code&redirect_uri={settings.domain}{settings.ok.redirect_uri}&layout=m&state={telegram_id}", 
        status_code=301
    )

@router.get("/ok_callback")
async def ok_callback(request: Request):
    try:
        params = dict(request.query_params)
        OAuthCallbackData(**params)
    except Exception:
        return HTTPException(status_code=422, detail="Страница не найдена")
    
    code = params.get("code")
    state = int(params.get("state"))

    redirect_uri = settings.domain + settings.ok.redirect_uri
    data = await ok_exchange_code_to_access(
        code=code,
        redirect_uri=redirect_uri,
        client_id=settings.ok.client_id,
        client_secret=settings.ok.client_secret
    )
    access_token = data.get("access_token")
    refresh_token = data.get("refresh_token")

    
    # сохранить refresh
    db = request.state.db_container
    await db.user_service.set_ok_refresh(telegram_id=state, token=refresh_token)
    await db.session.commit()
    
    # валидация
    ok_user_id = await ok_get_user_id(
        access_token=access_token,
        application_secret_key=settings.ok.client_secret,
        application_public_key=settings.ok.client_public,
    )
    logger.info(f"exchange success, tg={state}, ok user id = {ok_user_id}")
    if ok_user_id:
        await db.user_service.set_ok_user_id(telegram_id=state, ok_user_id=ok_user_id)
        await db.session.commit()
    return templates.TemplateResponse(
        "ok_deeplink.html",
        {
            "request": request,
            "group_id": settings.ok.group_id
        }
    )

    
@router.post("/webhook")
async def webhook(request: Request) -> None:
    logger.info("Received webhook request")
    update = await request.json()
    dp = request.state.tg_dispatcher
    bot = request.state.tg_bot
    asyncio.create_task(dp.feed_raw_update(bot, update))
    logger.info("Update processed")