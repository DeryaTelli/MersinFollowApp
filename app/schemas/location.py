from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional

class LocationIn(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)

class LocationOut(BaseModel):
    user_id: int
    lat: float
    lon: float
    created_at: datetime

class LastLocation(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    lat: float
    lon: float
    created_at: datetime

class DayQuery(BaseModel):
    day: date

class LocationUpdate(BaseModel):
    lat: Optional[float] = Field(None, ge=-90, le=90)
    lon: Optional[float] = Field(None, ge=-180, le=180)
    # created_at'i güncellersen day alanı yeniden hesaplanacak
    created_at: Optional[datetime] = None