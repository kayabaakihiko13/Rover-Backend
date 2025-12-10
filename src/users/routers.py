from datetime import timedelta
from fastapi import (
    APIRouter, Depends, HTTPException, status
)
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import jwt, JWTError

# import local  module
from src.users.models import User
from src.users.schemas import (
    UserRegister, UserResponse, TokenResponse,
    ForgetPasswordRequest, ResetPasswordRequest
)
from src.core.db import get_db
from src.core.auth import (
    oauth2_scheme, hash_password, verify_password,
    create_access_token
)
from src.core.config import settings


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ======== GET CURRENT USER (DECODE JWT) ==========
def _get_current_user(token: str = Depends(oauth2_scheme),
                      db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY_JWT,
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.user_id == str(user_id)).first()
    if not user:
        raise credentials_exception
    return user


# ========== REGISTER USER ==========
@router.post("/register", response_model=UserResponse)
async def register_user(user: UserRegister, db: Session = Depends(get_db)):
    # cek email unik
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # cek username unik
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # hash password
    hashed_pw = hash_password(user.password)
    db_user = User(
        firstname=user.firstname,
        lastname=user.lastname,
        username=user.username,
        email=user.email,
        password=hashed_pw,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# ========== LOGIN USER ==========
@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ========== FORGOT PASSWORD ==========
@router.post("/forgot-password")
async def forgot_password(request: ForgetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_access_token(
        data={"sub": str(user.user_id), "reset": True},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    reset_link = f"http://localhost:8000/users/reset-password?token={reset_token}"
    print("Send this link to user via email:", reset_link)

    return {
        "message": "Password reset link generated successfully",
        "reset_link": reset_link,
    }


# ========== RESET PASSWORD ==========
@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(
            request.token,
            settings.SECRET_KEY_JWT,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if not payload.get("reset"):
            raise HTTPException(status_code=400, detail="Invalid token type")
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if request.new_password != request.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    if verify_password(request.new_password, user.password):
        raise HTTPException(
            status_code=400,
            detail="New password cannot be the same as the old one"
        )

    user.password = hash_password(request.new_password)
    db.commit()

    return {"message": "Password reset successful"}
