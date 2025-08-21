from sqlalchemy.orm import Session
from sqlalchemy import select
from app.domain.user import User , Role

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalar(select(User).where(User.email == email))


    def get_by_id(self, user_id: int) -> User | None:  # NEW
        return self.db.get(User, user_id)


    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User, hard: bool = False):
        if hard:
            self.db.delete(user)
        else:
            user.is_active = False
            self.db.add(user)
        self.db.commit()

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


  # NEW: role filtreli liste
    def list_by_role(self, role: Role | None = None) -> list[User]:
        stmt = select(User).where(User.is_active == True)
        if role:
            stmt = stmt.where(User.role == role)
        return list(self.db.scalars(stmt))