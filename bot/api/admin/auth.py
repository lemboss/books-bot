import hmac
import time
import json
import hashlib
import urllib.parse
from fastapi import Header, HTTPException, status
from .schemas import TelegramUser
from config import settings

# сколько времени считаем сессию валидной (можно увеличить/уменьшить)
WEBAPP_AUTH_TTL_SECONDS = 24 * 60 * 60  # 24 часа


def _check_telegram_init_data(init_data: str) -> TelegramUser:
    """
    Проверка подписи initData по алгоритму Telegram WebApp.
    Документация: https://core.telegram.org/bots/webapps#validating-data-received-via-the-web-app
    init_data приходит строкой вида: "auth_date=...&query_id=...&user={...}&hash=..."
    """

    # Разбираем как query string
    parsed = urllib.parse.parse_qs(init_data, strict_parsing=True)

    # Превращаем список значений в одно значение
    data = {k: v[0] for k, v in parsed.items()}

    received_hash = data.pop("hash", None)
    if not received_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing hash in init data",
        )

    # auth_date проверяем на "просрочку"
    auth_date_str = data.get("auth_date")
    if not auth_date_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing auth_date in init data",
        )

    try:
        auth_date = int(auth_date_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid auth_date format",
        )

    now_ts = int(time.time())
    if now_ts - auth_date > WEBAPP_AUTH_TTL_SECONDS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="WebApp auth data expired",
        )

    # Формируем data_check_string
    # Берём пары key=value, сортируем по key, соединяем \n
    data_check_arr = [f"{k}={v}" for k, v in sorted(data.items())]
    data_check_string = "\n".join(data_check_arr)

    # Секретный ключ
    secret_key = hmac.new(
        key="WebAppData".encode("utf-8"),
        msg=settings.tgbot.token.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    # Считаем свой hash
    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid init data hash",
        )

    # Если подпись ок, вытаскиваем user
    user_json_str = data.get("user")
    if not user_json_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No user in init data",
        )

    try:
        user_data = json.loads(user_json_str)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user JSON",
        )

    # проверка, что user.id в списке админов
    if user_data["id"] not in settings.tgbot.admins:
        raise HTTPException(status_code=403, detail="Not an admin")

    return TelegramUser(**user_data)


async def get_current_telegram_user(
    init_data: str = Header(..., alias="X-Telegram-Init-Data"),
) -> TelegramUser:
    """
    FastAPI dependency.
    Берёт initData из заголовка X-Telegram-Init-Data,
    проверяет подпись и возвращает TelegramUser.
    """
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Telegram-Init-Data header",
        )

    return _check_telegram_init_data(init_data)