# server/app/schemas/user.py

from pydantic import BaseModel


class UserRegister(BaseModel):
    name: str
    phone: str
    password: str
    preferred_language: str = "en"


class UserLogin(BaseModel):
    phone: str
    password: str


class UserResponse(BaseModel):
    user_id: str
    token: str