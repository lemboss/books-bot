from datetime import datetime
import pytest
from bot.infrastructure.database.models import User

@pytest.fixture(autouse=True)
async def seed_users(session):
    # session.add_all([
    #     User(id=1, firstname="a"),
    #     User(id=443587978, referrer_id=None),
    #     User(id=443587979, referrer_id=443587978),
    #     User(id=443587980, referrer_id=443587978),
    #     User(id=443587981, referrer_id=443587978),
    # ])
    await session.commit()

# @pytest.mark.parametrize(
#     "telegram_id, referer_id", 
#     [
#         (10, None),
#         (11, 443587981),
#     ]
# )
# async def test_register_user(db_container, session, telegram_id, referer_id):
#     service = db_container.user_service
#     user = await service.add_in_system(telegram_id=telegram_id, referer_id=referer_id)
#     assert user
#     assert user.id == telegram_id
#     await session.commit()
#     user = await service.user_repo.get(telegram_id)
#     assert user
#     assert user.id == telegram_id
#     assert user.referrer_id == referer_id
