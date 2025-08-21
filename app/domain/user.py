from sqlalchemy import String, Enum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum
from app.db.base import Base

class Gender(PyEnum):
    male = "male"
    female = "female"

class Role(PyEnum):  # NEW
    admin = "admin"
    user = "user"



class User(Base):
    __tablename__ = "users" #veritabanindaki tablo adi

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    gender: Mapped[Gender] = mapped_column(Enum(Gender), default=Gender.male)
    # “Tokeni kendim gireceğim” dediğiniz için opsiyonel server-tanımlı token alanı:
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user)
    server_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
