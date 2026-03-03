from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.core.db import get_db
from src.core.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_admin,
    admin_require_role,
)
from src.core.roles import RoleEnum
from src.admin.models import Admin
from src.admin.schemas import (
    AdminLogin,
    AdminCreate,
    AdminResponse,
    AdminUpdate,
    TokenResponse,
    UserInList,
    UserDetail,
    DashboardStats,
    AnalyticsResponse,
    GrowthData,
)
from src.users.models import User
from src.posts.models import Post
from src.admin.models import News

router = APIRouter(prefix="/admin", tags=["Admin"])


# ========== ADMIN LOGIN ==========
@router.post("/login", response_model=TokenResponse)
async def admin_login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    admin = db.query(Admin).filter(Admin.username == form_data.username).first()

    if not admin or not verify_password(form_data.password, admin.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin account is inactive"
        )

    access_token = create_access_token(
        data={"sub": str(admin.admin_id)},
        expires_delta=timedelta(minutes=60 * 24),  # 24 hours
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ========== CREATE ADMIN (Superadmin only) ==========
@router.post(
    "/register",
    response_model=AdminResponse,
    dependencies=[Depends(admin_require_role([RoleEnum.SUPERADMIN]))],
)
async def create_admin(
    admin_data: AdminCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    if admin_data.role not in ["superadmin", "moderator"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    if db.query(Admin).filter(Admin.email == admin_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    if db.query(Admin).filter(Admin.username == admin_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_pw = hash_password(admin_data.password)
    new_admin = Admin(
        email=admin_data.email,
        username=admin_data.username,
        password=hashed_pw,
        role=admin_data.role,
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    return new_admin


# ========== DASHBOARD STATS ==========
@router.get(
    "/dashboard",
    response_model=DashboardStats,
    dependencies=[
        Depends(admin_require_role([RoleEnum.SUPERADMIN, RoleEnum.MODERATOR]))
    ],
)
async def get_dashboard(
    db: Session = Depends(get_db), current_admin: Admin = Depends(get_current_admin)
):
    total_users = db.query(User).count()
    total_posts = db.query(Post).count()
    total_news = db.query(News).count()
    active_users = (
        db.query(User).filter(User.is_active == True).count()
        if hasattr(User, "is_active")
        else total_users
    )
    banned_users = (
        db.query(User).filter(User.is_active == False).count()
        if hasattr(User, "is_active")
        else 0
    )

    return DashboardStats(
        total_users=total_users,
        total_posts=total_posts,
        total_news=total_news,
        active_users=active_users,
        banned_users=banned_users,
    )


# ========== ANALYTICS ==========
@router.get(
    "/analytics",
    response_model=AnalyticsResponse,
    dependencies=[
        Depends(admin_require_role([RoleEnum.SUPERADMIN, RoleEnum.MODERATOR]))
    ],
)
async def get_analytics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    start_date = datetime.utcnow() - timedelta(days=days)

    user_growth_data = (
        db.query(
            func.date(User.create_at).label("date"),
            func.count(User.user_id).label("count"),
        )
        .filter(User.create_at >= start_date)
        .group_by(func.date(User.create_at))
        .all()
    )

    post_growth_data = (
        db.query(
            func.date(Post.create_at).label("date"),
            func.count(Post.post_id).label("count"),
        )
        .filter(Post.create_at >= start_date)
        .group_by(func.date(Post.create_at))
        .all()
    )

    news_growth_data = (
        db.query(
            func.date(News.create_at).label("date"),
            func.count(News.news_id).label("count"),
        )
        .filter(News.create_at >= start_date)
        .group_by(func.date(News.create_at))
        .all()
    )

    user_growth = [
        GrowthData(date=str(row.date), count=row.count) for row in user_growth_data
    ]
    post_growth = [
        GrowthData(date=str(row.date), count=row.count) for row in post_growth_data
    ]
    news_growth = [
        GrowthData(date=str(row.date), count=row.count) for row in news_growth_data
    ]

    return AnalyticsResponse(
        user_growth=user_growth, post_growth=post_growth, news_growth=news_growth
    )


# ========== LIST USERS (Superadmin only) ==========
@router.get(
    "/users",
    response_model=list[UserInList],
    dependencies=[Depends(admin_require_role([RoleEnum.SUPERADMIN]))],
)
async def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users


# ========== GET USER DETAIL (Superadmin only) ==========
@router.get(
    "/users/{user_id}",
    response_model=UserDetail,
    dependencies=[Depends(admin_require_role([RoleEnum.SUPERADMIN]))],
)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# ========== DELETE/BAN USER (Superadmin only) ==========
@router.delete(
    "/users/{user_id}",
    dependencies=[Depends(admin_require_role([RoleEnum.SUPERADMIN]))],
)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if hasattr(user, "is_active"):
        user.is_active = False
        db.commit()
        return {"message": "User has been banned"}
    else:
        db.delete(user)
        db.commit()
        return {"message": "User has been deleted"}
