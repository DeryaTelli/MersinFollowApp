from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api.v1.users import router as users_router
from app.api.v1 import tracking



def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Auth")
    app.include_router(users_router)
    app.include_router(tracking.router)
    return app

app = create_app()

# İlk çalıştırmada tabloları oluştur
Base.metadata.create_all(bind=engine)

