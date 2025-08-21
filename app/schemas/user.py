from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from typing import Optional

class Gender(str, Enum):
    male = "male"
    female = "female"

class Role(str, Enum):  # NEW
    admin = "admin"
    user = "user"


class UserCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(min_length=6)
    gender: Gender
    role: Role = Role.user
    server_token: str | None = None  # Admin panelinden/set edilebilir

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    gender: Gender
    role: Role
    server_token: str | None

    class Config:
        from_attributes = True  # SQLAlchemy objesinden okunabilsin

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str]  = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str]   = Field(None, min_length=6)
    gender: Optional[Gender]  = None
    role: Optional[Role]      = None
    server_token: Optional[str] = None
    is_active: Optional[bool] = None
