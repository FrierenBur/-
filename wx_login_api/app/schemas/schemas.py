from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WechatLoginRequest(BaseModel):
    code: str
    user_info: Optional[dict] = None

class UserInfo(BaseModel):
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    gender: Optional[int] = None
    country: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    openid: str
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    openid: Optional[str] = None