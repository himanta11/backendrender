from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str