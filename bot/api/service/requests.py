import logging
import aiohttp
import hashlib

logger = logging.getLogger(__name__)

async def vk_exchange_code_to_access(
        state,
        code,
        device_id,
        redirect_url,
        client_id,
        code_verifier
    ):
    url = "https://id.vk.ru/oauth2/auth"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
        "code": code,
        "device_id": device_id,
        "redirect_uri": redirect_url,
        "client_id": client_id, 
        "state": state
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=payload) as response:
            status = response.status
            data = await response.json()
            return data

async def ok_exchange_code_to_access(
        code,
        redirect_uri,
        client_id,
        client_secret
    ):
    url = "https://api.ok.ru/oauth/token.do"
    params = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as response:
            status = response.status
            data = await response.json()
            return data



async def ok_get_user_id(
        access_token,
        application_secret_key,
        application_public_key
    ):
    url = "https://api.ok.ru/fb.do"
    
    secret_key = hashlib.md5((access_token+application_secret_key).encode()).hexdigest()
    params = {
        "application_key": application_public_key, 
        "format": "json",
        "method": "users.getLoggedInUser"
    }

    sig_source = "".join([f"{k}={v}" for k, v in sorted(params.items())]) + secret_key
    sig = hashlib.md5(sig_source.encode()).hexdigest()

    params.setdefault("sig", sig)
    params.setdefault("access_token", access_token)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as response:
                status = response.status
                data = await response.json()
                return int(data)
    except Exception:
        return None


