from sqlalchemy import text, BIGINT, Integer
from sqlalchemy.orm import mapped_column
from typing import Annotated
import datetime

bigint_pk = Annotated[int, mapped_column(BIGINT, primary_key=True)]
int_pk = Annotated[int, mapped_column(Integer, primary_key=True)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('Europe/Moscow', now())"))]
updated_at = Annotated[
    datetime.datetime, 
    mapped_column(
        server_onupdate=text("TIMEZONE('Europe/Moscow', now())"),
        server_default=text("TIMEZONE('Europe/Moscow', now())"),
    )
]