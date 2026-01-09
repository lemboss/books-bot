import aiohttp

async def vk_group_is_member(group_id: str, group_token: str, vk_user_id: int | None):
    if vk_user_id is None:
        return False
    
    uri = f"https://api.vk.ru/method/groups.isMember"
    headers = {
        "Authorization": "Bearer " + group_token
    }
    params = {
        "group_id": group_id,
        "user_id": vk_user_id,
        "v": "5.199"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(uri, headers=headers, params=params) as response:
            data = await response.json()
            print(data)
            if str(data.get("response")) == "1":
                return True
            else:
                return False