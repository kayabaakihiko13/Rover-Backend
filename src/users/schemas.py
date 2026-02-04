from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import Optional,Any

# User Schemas
class UserRegister(BaseModel):
    firstname:str
    lastname:str
    username:str
    email:str
    password:str


class UserLogin(BaseModel):
    username:str
    password:str

class UserResponse(BaseModel):
    user_id:str
    firstname:str
    lastname:str
    username:str
    email:str

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ForgetPasswordRequest(BaseModel):
    username: str

class ResetPasswordRequest(BaseModel):
    token:str
    new_password: str
    confirm_password: str