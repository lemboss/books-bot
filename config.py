from dataclasses import dataclass
from environs import Env
import logging

@dataclass
class DB:
    host: str
    port: int
    database: str
    user: str
    password: str

    @property
    def url(self):
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
    
@dataclass
class TGBot:
    token: str
    admins: list[int]

# @dataclass
# class Redis:
#     url: str
#     host: str
#     port: int

    
@dataclass
class Config:
    mode: bool
    domain: str
    db: DB
    # redis: Redis
    tgbot: TGBot
    
def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    mode = env('MODE')
    if env('MODE') not in ("TEST", "DEV", "PROD"):
        raise Exception
    
    db_prefix = "TEST_" if mode == "TEST" else ""

    tgbot_admins = list(map(lambda x: int(x) if x.isdigit() else 0, env("TGBOT_ADMINS").split(",")))
    settings = Config(
        mode=mode,
        domain=env('DOMAIN'),
        db=DB(
            host=env(db_prefix+'DB_HOST'),
            port=env(db_prefix+'DB_PORT'),
            database=env(db_prefix+'DB_NAME'),
            user=env(db_prefix+'DB_USER'),
            password=env(db_prefix+'DB_PASS'),
        ),
        # redis=Redis(
        #     host=env("REDIS_HOST"),
        #     port=int(env("REDIS_PORT")),
        #     url=f"redis://{env('REDIS_HOST')}:{env("REDIS_PORT")}",
        # ),
        tgbot=TGBot(
            token=env("TGBOT_TOKEN"),
            admins=tgbot_admins,
        )
    )
    
    if settings.mode in ("DEV", "TEST"):
        logging.basicConfig(level=logging.DEBUG, #filename="logs.log",filemode="a",
                    format='[%(asctime)s] #%(levelname)-8s %(filename)s:' '%(lineno)d - %(name)s - %(message)s')   
    else:
        logging.getLogger("aiogram").setLevel(logging.ERROR)
        logging.getLogger("aiohttp").setLevel(logging.ERROR)
        logging.basicConfig(level=logging.INFO, filename="./logs/logs.log",filemode="a",
                    format='[%(asctime)s] #%(levelname)-8s %(filename)s:' '%(lineno)d - %(name)s - %(message)s')   
        
    return settings

settings = load_config()