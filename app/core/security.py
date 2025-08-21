from datetime import datetime, timedelta, timezone
from jose import jwt , JWTError
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.core.config import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
# parolari 'bcrypt' semasiyla hash'lemek dogrulamak ivin kullanilir

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)
#kullanicinin duz parolasini guclu bir sekilde hashler


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)
#girilen duz parola veritabanindaki hash ile uyusuyormu kontrol eder

def create_access_token(sub: str, *, extra: dict | None = None, expires_minutes: int | None = None) -> str:
   #sub: token kimin icinse id veya eposta
   #extra: tokene ek roller izinler koymak icin verilir
   # expires_minutes : varsayilan surenin token suresinin uzerine gecmek istersen dakikayi buraya verebilirsin
    to_encode = {"sub": sub, "iat": int(datetime.now(tz=timezone.utc).timestamp())}
   # iat (issued at): tokenin olusturuldu an
    if extra:
        to_encode.update(extra)
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
   # tokenin sone erme zamani hesaplanliyo
    to_encode.update({"exp": expire})
   #token su zamana kadar gecerli
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
   #payload (to_encode) belirtilen secret ve algoritme hs256 ile imzalanalir
   #sonuc string jwt


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")