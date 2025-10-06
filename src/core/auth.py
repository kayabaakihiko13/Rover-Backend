from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
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
