from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class UserOut(BaseModel):
    id: int
    telegram_id: Optional[int]
    username: Optional[str]
    count_referrals: int
    count_aviable_songs: int
    count_generated_songs: int
    avg_grade: Optional[float]
    created_at: datetime


class UsersResponse(BaseModel):
    users: List[UserOut]
    total: Optional[int]
    offset: int
    limit: int


class PromoCodeItem(BaseModel):
    id: int
    code: str
    bonus_songs: int
    valid_until: Optional[datetime]
    is_active: bool
    created_at: datetime


class PromoCodesResponse(BaseModel):
    items: List[PromoCodeItem]
    total: int
    offset: int
    limit: int


class PromoCodeCreateRequest(BaseModel):
    code: str
    bonus_songs: int = 1
    valid_until: Optional[datetime] = None
    is_active: bool = True
    
class SongLogItem(BaseModel):
    telegram_id: str        
    initiator: str            
    msg: str
    created_at: datetime   
    
class SongLogsResponse(BaseModel):
    logs: List[SongLogItem]
    total: int
    offset: int
    limit: int


class SongAudioResponse(BaseModel):
    id: str
    title: str
    url: str

class BroadcastMessageIn(BaseModel):
    text: str = Field(..., min_length=1, description="Текст сообщения")
    user_ids: List[int] = Field(..., min_items=1, description="Список ID пользователей")
    
class BroadcastItem(BaseModel):
    id: int
    text: str
    is_sent: bool
    count_users: int
    count_success_delivered: int
    created_at: datetime

class BroadcastsResponse(BaseModel):
    broadcasts: List[BroadcastItem]
    total: int
    offset: int
    limit: int
    
class LetSongRequest(BaseModel):
    telegram_id: int
    count: int
    

class LetSongResponse(BaseModel):
    success: bool
    detail: Optional[str] = None
    
    
class TelegramUser(BaseModel):
    id: int
    is_bot: Optional[bool] = False
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None