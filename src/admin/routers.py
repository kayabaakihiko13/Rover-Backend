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
    HarvestInList,
    DashboardAnalytics,
    CategoryCount,
    UserEarnings,
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

    total_harvests = 0
    posts = db.query(Post).all()
    for post in posts:
        if post.result and "counters" in post.result:
            for count in post.result.get("counters", []):
                total_harvests += count

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
        total_harvests=total_harvests,
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

    user_growth = [
        GrowthData(date=str(row.date), count=int(row.count)) for row in user_growth_data
    ]

    posts = db.query(Post).all()

    category_map = {
        "matang": {"name": "Matang", "count": 0, "price": 5000},
        "abnormal": {"name": "Abnormal", "count": 0, "price": 0},
        "kosong": {"name": "Kosong", "count": 0, "price": 0},
        "mentah": {"name": "Mentah", "count": 0, "price": 2000},
        "setangah_matang": {"name": "Setengah Matang", "count": 0, "price": 3000},
        "terlalu_matang": {"name": "Terlalu Matang", "count": 0, "price": 1000},
    }

    user_earnings_map = {}

    for post in posts:
        if post.result and "labels" in post.result and "counters" in post.result:
            labels = post.result.get("labels", [])
            counters = post.result.get("counters", [])
            for label, counter in zip(labels, counters):
                label_lower = label.lower().strip()
                if label_lower in category_map:
                    category_map[label_lower]["count"] += counter
                    earnings = counter * category_map[label_lower]["price"]
                    if post.user_id not in user_earnings_map:
                        user_earnings_map[post.user_id] = 0
                    user_earnings_map[post.user_id] += earnings

    categories = []
    total_earnings = 0
    for key, data in category_map.items():
        total = data["count"] * data["price"]
        total_earnings += total
        categories.append(
            CategoryCount(
                name=data["name"],
                count=data["count"],
                price=data["price"],
                total=total,
            )
        )

    users = db.query(User).all()
    user_earnings = []
    for user in users:
        earnings = user_earnings_map.get(user.user_id, 0)
        user_earnings.append(
            UserEarnings(
                user_id=user.user_id,
                username=user.username,
                total_earnings=earnings,
            )
        )

    return AnalyticsResponse(
        user_growth=user_growth,
        categories=categories,
        total_earnings=total_earnings,
        user_earnings=user_earnings,
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


# ========== LIST ALL HARVESTS (Superadmin/Moderator) ==========
@router.get(
    "/harvests",
    response_model=list[HarvestInList],
    dependencies=[
        Depends(admin_require_role([RoleEnum.SUPERADMIN, RoleEnum.MODERATOR]))
    ],
)
async def list_harvests(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    posts = (
        db.query(Post, User)
        .join(User, Post.user_id == User.user_id)
        .order_by(Post.create_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for post, user in posts:
        result.append(
            HarvestInList(
                post_id=post.post_id,
                user_id=post.user_id,
                username=user.username,
                firstname=user.firstname,
                lastname=user.lastname,
                image_url=post.image_url,
                result=post.result,
                create_at=post.create_at,
            )
        )

    return result


# ========== DELETE POST (Superadmin/Moderator) ==========
@router.delete(
    "/posts/{post_id}",
    dependencies=[
        Depends(admin_require_role([RoleEnum.SUPERADMIN, RoleEnum.MODERATOR]))
    ],
)
async def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    post = db.query(Post).filter(Post.post_id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()
    return {"message": "Post has been deleted"}
