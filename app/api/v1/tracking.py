from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, require_admin_jwt
from app.domain.user import User as UserEntity, Role
from app.repositories.location_repo import LocationRepository
from app.schemas.location import LocationIn, LocationOut, LastLocation
from app.ws.manager import manager
from app.core.security import decode_access_token
from app.schemas.location import LocationUpdate, LocationOut
from app.api.deps import get_db, require_admin_key

router = APIRouter(prefix="/tracking", tags=["tracking"])

# ---- REST Fallback (opsiyonel): mobil konum POST
@router.post("/point", response_model=LocationOut)
def post_point(payload: LocationIn, db: Session = Depends(get_db), me: UserEntity = Depends(get_current_user)):
    repo = LocationRepository(db)
    p = repo.save_point(me.id, payload.lat, payload.lon)
    return {"user_id": me.id, "lat": p.lat, "lon": p.lon, "created_at": p.created_at}

# ---- REST: kendi günün noktaları (user)
@router.get("/my/day", response_model=list[LocationOut])
def my_day(day: date = Query(...), db: Session = Depends(get_db), me: UserEntity = Depends(get_current_user)):
    repo = LocationRepository(db)
    pts = repo.list_points_for_day(me.id, day)
    return [{"user_id": me.id, "lat": p.lat, "lon": p.lon, "created_at": p.created_at} for p in pts]

# ---- REST: admin için snapshot (tüm user'ların son konumu)
@router.get("/admin/last", response_model=list[LastLocation])
def admin_last(db: Session = Depends(get_db), _admin: UserEntity = Depends(require_admin_jwt)):
    repo = LocationRepository(db)
    rows = repo.last_points_for_all_users()
    out = []
    for u, p in rows:
        out.append({"user_id": u.id, "first_name": u.first_name, "last_name": u.last_name,
                    "lat": p.lat, "lon": p.lon, "created_at": p.created_at})
    return out



# --- Tek bir noktayı GÜNCELLE (kendi noktası veya admin)
@router.patch("/points/{point_id}", response_model=LocationOut)
def update_point_admin(
    point_id: int,
    payload: LocationUpdate,
    db: Session = Depends(get_db),
    _ok: bool = Depends(require_admin_key),             # X-Admin-Key
):
    repo = LocationRepository(db)
    p = repo.get_by_id(point_id)
    if not p:
        raise HTTPException(status_code=404, detail="Point not found")
    p = repo.update_point(p, lat=payload.lat, lon=payload.lon, created_at=payload.created_at)
    return {"user_id": p.user_id, "lat": p.lat, "lon": p.lon, "created_at": p.created_at}

# --- Admin: belirli kullanıcının GÜNÜNÜ LİSTELE (tüm noktalar) [GET]
@router.get("/admin/users/{user_id}/day", response_model=list[LocationOut])
def admin_user_day(
    user_id: int,
    day: date = Query(...),
    db: Session = Depends(get_db),
    _admin: UserEntity = Depends(require_admin_jwt),  # Admin JWT ile koru
):
    repo = LocationRepository(db)
    pts = repo.list_points_for_day(user_id, day)
    return [
        {
            "user_id": user_id,
            "lat": p.lat,
            "lon": p.lon,
            "created_at": p.created_at,
        }
        for p in pts
    ]



# --- Admin: belirli kullanıcının gününü sil
@router.delete("/admin/{user_id}/day", status_code=status.HTTP_200_OK)
def admin_delete_user_day(
    user_id: int,
    day: date = Query(...),
    db: Session = Depends(get_db),
    _ok: bool = Depends(require_admin_key),             #  X-Admin-Key
):
    repo = LocationRepository(db)
    count = repo.delete_points_for_day(user_id, day)
    return {"deleted": count}



# ---- WS auth yardımcı
async def _auth_ws_token(raw_token: str) -> dict:
    # raw_token = "...jwt..."
    payload = decode_access_token(raw_token)
    return payload

# ---- WS: kullanıcı konum gönderir
@router.websocket("/ws/track")
async def ws_track(websocket: WebSocket, token: str):
    payload = await _auth_ws_token(token)
    user_id = int(payload.get("sub", "0"))
    role = payload.get("role")
    if role not in ("user", "admin"):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION); return

    await manager.connect_user(user_id, websocket)
    print(f"[WS] user {user_id} connected")
    try:
        while True:
            data = await websocket.receive_json()
            print("WS recv:", data)

            # 🔧 HEM type HEM event destekle
            kind = data.get("type") or data.get("event")
            if kind != "loc":
                # istersen ping/pong vb. başka event’leri de burada ele al
                continue

            lat = float(data["lat"])
            lon = float(data["lon"])

            # DB'ye yaz
            from app.db.session import SessionLocal
            db: Session = SessionLocal()
            try:
                repo = LocationRepository(db)
                p = repo.save_point(user_id, lat, lon, datetime.now(timezone.utc))
                print(f"DB saved: uid={user_id} id={p.id} at=({lat},{lon})")
            finally:
                db.close()

            # adminlere canlı yayın
            await manager.broadcast_to_admins({
                "event": "loc",
                "user_id": user_id,
                "lat": lat, "lon": lon,
                "created_at": p.created_at.isoformat()
            })

            # küçük ACK
            await websocket.send_json({"event": "ack", "ok": True})
    except Exception as e:
        # Hata yakalamayı boş bırakma; en azından logla
        print("ws_track error:", e)
    finally:
        manager.disconnect_user(user_id, websocket)
        print(f"[WS] user {user_id} connected")

    # ---- WS: admin canlı dinler
@router.websocket("/ws/admin")
async def ws_admin(websocket: WebSocket, token: str):
    payload = await _auth_ws_token(token)
    role = payload.get("role")
    if role != "admin":
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION); return

    await manager.connect_admin(websocket)

    # bağlanınca snapshot gönder
    from app.db.session import SessionLocal
    db: Session = SessionLocal()
    try:
        repo = LocationRepository(db)
        rows = repo.last_points_for_all_users()
        await websocket.send_json({
            "event": "snapshot",
            "items": [
                {"user_id": u.id, "first_name": u.first_name, "last_name": u.last_name,
                 "lat": p.lat, "lon": p.lon, "created_at": p.created_at.isoformat()}
                for u, p in rows
            ]
        })
    finally:
        db.close()

    try:
        # admin WS'den gelen mesajları şimdilik yok say
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        manager.disconnect_admin(websocket)
