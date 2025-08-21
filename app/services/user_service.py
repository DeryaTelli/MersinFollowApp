from sqlalchemy.orm import Session
from app.domain.user import User, Gender as GenderDomain, Role as RoleDomain
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserUpdate

class UserService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register_user(self, data: UserCreate) -> User:
        if self.repo.get_by_email(data.email):
            raise ValueError("Email already in use.")
        entity = User(
            first_name=data.first_name,
            last_name=data.last_name,
            email=data.email,
            password_hash=hash_password(data.password),
            gender=GenderDomain(data.gender),
            role=RoleDomain(data.role),
            server_token=data.server_token,  # “kendim gireceğim” derseniz buradan verilir
        )
        return self.repo.create(entity)

    def update_user(self, user: User, data: UserUpdate) -> User:
        if data.email and self.repo.get_by_email(data.email) and data.email != user.email:
            raise ValueError("Email already in use.")
        if data.first_name is not None: user.first_name = data.first_name
        if data.last_name is not None: user.last_name = data.last_name
        if data.email is not None: user.email = data.email
        if data.password is not None: user.password_hash = hash_password(data.password)
        if data.gender is not None: user.gender = data.gender.value if hasattr(data.gender, 'value') else data.gender
        if data.role is not None: user.role = data.role.value if hasattr(data.role, 'value') else data.role
        if data.server_token is not None: user.server_token = data.server_token
        if data.is_active is not None: user.is_active = data.is_active
        return self.repo.save(user)

    def authenticate(self, email: str, password: str) -> str:
        user = self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash) or not user.is_active:
            raise ValueError("Invalid credentials.")
        # Flutter bu JWT ile giriş yapacak
        return create_access_token(str(user.id), extra={"email": user.email, "role": user.role.value} )

