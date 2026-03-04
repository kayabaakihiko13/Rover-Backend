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
    role: str


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
    total_harvests: int
    active_users: int
    banned_users: int


class GrowthData(BaseModel):
    date: str
    count: int


class CategoryCount(BaseModel):
    name: str
    count: int
    price: int
    total: int


class UserEarnings(BaseModel):
    user_id: str
    username: str
    total_earnings: int


class AnalyticsResponse(BaseModel):
    user_growth: list[GrowthData]
    categories: list[CategoryCount]
    total_earnings: int
    user_earnings: list[UserEarnings]


class HarvestInList(BaseModel):
    post_id: str
    user_id: str
    username: str
    firstname: str
    lastname: str
    image_url: str
    result: Optional[dict] = None
    create_at: datetime

    class Config:
        from_attributes = True


class DashboardAnalytics(BaseModel):
    user_growth: list[GrowthData]
    total_users: int
    total_posts: int
    total_harvests: int
    total_earnings: int
    categories: list[CategoryCount]
    user_earnings: list[UserEarnings]
