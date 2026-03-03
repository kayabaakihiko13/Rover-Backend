from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class AdminLogin(BaseModel):
    username: str
    password: str


class AdminCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    role: str  # superadmin, moderator


class AdminResponse(BaseModel):
    admin_id: str
    email: str
    username: str
    role: str
    is_active: bool
    create_at: datetime

    class Config:
        from_attributes = True


class AdminUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserInList(BaseModel):
    user_id: str
    firstname: str
    lastname: str
    username: str
    email: str
    role: str
    is_active: bool
    create_at: datetime

    class Config:
        from_attributes = True


class UserDetail(BaseModel):
    user_id: str
    firstname: str
    lastname: str
    username: str
    email: str
    role: str
    is_active: bool
    create_at: datetime
    update_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_users: int
    total_posts: int
    total_news: int
    active_users: int
    banned_users: int


class GrowthData(BaseModel):
    date: str
    count: int


class AnalyticsResponse(BaseModel):
    user_growth: list[GrowthData]
    post_growth: list[GrowthData]
    news_growth: list[GrowthData]
