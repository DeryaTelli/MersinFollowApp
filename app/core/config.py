from pydantic import BaseModel , EmailStr
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv()
class Settings(BaseModel):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    # ortam degiskeninden gizli anahtar aliyor yoksa dev-secret-change-me varsayilani ataniyor
    #bu anahtar jwt tokanlerini imzalamak ve dogrulamak icin kullanilir
    JWT_ALG: str = "HS256"
    #jwtalg sabit olarak hs256 algoritmasini belirtiyor
    #b jwt tokenlarinin hangi algoritma ile imzalanacagini ifade eder
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 gün
    # tokenlerin gecerlilik suresini belirtiyor
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "change-me-admin-key")  # NEW


settings = Settings()