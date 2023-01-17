from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    send_alerts: bool = True
    mastodon_acct: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime
    is_active: bool
    is_admin: bool
    send_alerts: bool
    mastodon_acct: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ApiToken(BaseModel):
    user_id: int
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class MastodonUserCreate(BaseModel):    
    acct: str

class MastodonUserResponse(BaseModel):
    id: int
    acct: str
    created_at: datetime
    welcomed: bool
    welcomed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class PostResponse(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserResponse

    class Config:
        orm_mode = True

class PostOut(BaseModel):
    Post: PostResponse

    class Config:
        orm_mode = True    