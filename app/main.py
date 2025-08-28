from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
from app.api.v1.users import router as users_router
from app.api.v1 import tracking
from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(title="FastAPI Auth")
    app.include_router(users_router)
    app.include_router(tracking.router)

    # CORS middleware burada ekleniyor
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # prod ortamında buraya domainlerini yaz
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    return app


app = create_app()

# İlk çalıştırmada tabloları oluştur
Base.metadata.create_all(bind=engine)