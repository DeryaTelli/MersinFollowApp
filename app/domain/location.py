from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Float, Integer, DateTime, Date, ForeignKey, func, Index
from app.db.base import Base

class LocationPoint(Base):
    __tablename__ = "location_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    day: Mapped[Date] = mapped_column(Date, index=True)

Index("ix_user_day", LocationPoint.user_id, LocationPoint.day)
