from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from datetime import datetime, date, timezone
from app.domain.location import LocationPoint
from app.domain.user import User, Role

def _ensure_utc(dt: datetime) -> datetime:
    """Naive gelirse UTC varsay, aware ise UTC'ye çevir."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

class LocationRepository:
    def __init__(self, db: Session):
        self.db = db

    def save_point(self, user_id: int, lat: float, lon: float, when: datetime | None = None) -> LocationPoint:
        when = when or datetime.utcnow()
        obj = LocationPoint(user_id=user_id, lat=lat, lon=lon, created_at=when, day=when.date())
        self.db.add(obj); self.db.commit(); self.db.refresh(obj)
        return obj

    def get_by_id(self, point_id: int) -> LocationPoint | None:
        return self.db.get(LocationPoint, point_id)

    def list_points_for_day(self, user_id: int, day: date) -> list[LocationPoint]:
        stmt = select(LocationPoint).where(
            and_(LocationPoint.user_id == user_id, LocationPoint.day == day)
        ).order_by(LocationPoint.created_at.asc())
        return list(self.db.scalars(stmt))

    def delete_point(self, point: LocationPoint):
        self.db.delete(point);
        self.db.commit()

    def delete_points_for_day(self, user_id: int, day: date) -> int:
        pts = self.list_points_for_day(user_id, day)
        for p in pts: self.db.delete(p)
        self.db.commit()
        return len(pts)

    def update_point(self, point: LocationPoint, *, lat: float | None = None, lon: float | None = None,
                     created_at: datetime | None = None) -> LocationPoint:
        if lat is not None: point.lat = lat
        if lon is not None: point.lon = lon
        if created_at is not None:
            point.created_at = created_at
            point.day = created_at.date()
        self.db.add(point);
        self.db.commit();
        self.db.refresh(point)
        return point


    def last_point_for_user(self, user_id: int) -> LocationPoint | None:
        stmt = select(LocationPoint).where(LocationPoint.user_id == user_id)\
                                    .order_by(LocationPoint.created_at.desc()).limit(1)
        return self.db.scalar(stmt)

    def last_points_for_all_users(self) -> list[tuple[User, LocationPoint]]:
        # aktif tüm user'lar için son nokta
        users = list(self.db.scalars(select(User).where(User.role == Role.user, User.is_active == True)))
        out = []
        for u in users:
            last = self.last_point_for_user(u.id)
            if last: out.append((u, last))
        return out
