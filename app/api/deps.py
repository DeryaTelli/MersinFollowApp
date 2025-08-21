from typing import Generator
from fastapi import Header, HTTPException, status , Depends
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.security import decode_access_token
from app.repositories.user_repo import UserRepository
from app.domain.user import User as UserEntity, Role as RoleDomain



def get_db() -> Generator:
    db = SessionLocal() # yeni bir veritabani oturumu olusturur
    try:
        yield db # oturumu cagiran koda verir ornek olarak repository veya endpoint icinde kullanilmak uzere
    finally:
        db.close()  # is bitince oturum kapatilir

def require_admin_key(x_admin_key: str = Header(..., alias="X-Admin-Key")):  # NEW
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin key.")
    return True


def get_current_user(
    authorization: str | None = Header(None, alias="Authorization"),
    db = Depends(get_db),
):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    token = authorization.split(" ", 1)[1]
    payload = decode_access_token(token)
    user_id = int(payload.get("sub", "0"))
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    return user
def require_admin_jwt(current_user: UserEntity = Depends(get_current_user)):
    if current_user.role != RoleDomain.admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only.")
    return current_user
