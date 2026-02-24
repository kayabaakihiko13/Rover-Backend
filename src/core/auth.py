from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException,status
from jose import jwt,JWTError
from passlib.context import CryptContext
from src.core.db import get_db
from src.users.models import User
from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def hash_password(password: str) -> str:
    if not isinstance(password, str):
        password = str(password)
    password = password[:72]  # pastikan tidak lebih dari 72 bytes
    return pwd_context.hash(password)

def verify_password(plain_pw: str, hashed_pw: str) -> bool:
    if not isinstance(plain_pw, str):
        plain_pw = str(plain_pw)
    plain_pw = plain_pw[:72]  # bcrypt limit
    return pwd_context.verify(plain_pw, hashed_pw)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY_JWT, algorithm=settings.ALGORITHM)
# ======== GET CURRENT USER (DECODE JWT) ==========

def get_current_user(token: str = Depends(oauth2_scheme),
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

def create_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(minutes=15)

    payload = {
        "sub": email,
        "exp": expire,
        "type": "reset"
    }

    return jwt.encode(payload, settings.SECRET_KEY_JWT,
                      algorithm=settings.ALGORITHM)