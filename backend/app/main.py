from fastapi import FastAPI, Header, HTTPException
from uuid import UUID
from .db import get_conn
from .auth import verify_login, require_auth_header, init_shared_login_if_missing
from .schemas import LoginReq, SyncPushReq, ItemCreate, ItemUpdate

app = FastAPI(title="Store 3729 Inventory API")

@app.on_event("startup")
def _startup():
    init_shared_login_if_missing()

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/auth/login")
def login(req: LoginReq):
    token = verify_login(req.username, req.password)
    return {"token": token}

@app.post("/admin/change-login")
def change_login(req: LoginReq, authorization: str | None = Header(default=None)):
    require_auth_header(authorization)
    # Reuse init logic but force update
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
    with get_conn() as conn:
        conn.execute(
            "UPDATE auth_secrets SET username=%s, password_hash=%s, updated_at=now() WHERE id=1",
            (req.username, pwd.hash(req.password)),
        )
        conn.commit()
    return {"ok": True}

@app.get("/meta/settings")
def get_settings(authorization: str | None = Header(default=None)):
    require_auth_header(authorization)
    with get_conn() as conn:
        row = conn.execute("SELECT store_number, store_label, intersection FROM app_settings ORDER BY created_at ASC LIMIT 1").fetchone()
    if not row:
        return {"store_number": "3729", "store_label": "Sonic Drive-In #3729", "intersection": "Gilbert & Baseline"}
    return {"store_number": row[0], "store_label": row[1], "intersection": row[2]}

@app.get("/meta/units")
def get_units(authorization: str | None = Header(default=None)):
    require_auth_header(authorization)
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, active FROM units ORDER BY name ASC").fetchall()
    return [{"id": str(r[0]), "name": r[1], "active": r[2]} for r in rows]

@app.get("/meta/locations")
def get_locations(authorization: str | None = Header(default=None)):
    require_auth_header(authorization)
    with get_conn() as conn:
        rows = conn.execute("SELECT id, name, active FROM locations ORDER BY name ASC").fetchall()
    return [{"id": str(r[0]), "name": r[1], "active": r[2]} for r in rows]

@app.get("/items")
def list_items(authorization: str | None = Header(default=None), include_inactive: bool = False):
    require_auth_header(authorization)
    q = "SELECT id, name, base_unit_id, case_size, allow_partials, par_level, low_threshold, default_location_id, active FROM items"
    params = ()
    if not include_inactive:
        q += " WHERE active=true"
    q += " ORDER BY name ASC"
    with get_conn() as conn:
        rows = conn.execute(q, params).fetchall()
    return [{
        "id": str(r[0]),
        "name": r[1],
        "base_unit_id": str(r[2]),
        "case_size": float(r[3]) if r[3] is not None else None,
        "allow_partials": r[4],
        "par_level": float(r[5]) if r[5] is not None else None,
        "low_threshold": float(r[6]) if r[6] is not None else None,
        "default_location_id": str(r[7]) if r[7] is not None else None,
        "active": r[8],
    } for r in rows]

@app.post("/items")
def create_item(req: ItemCreate, authorization: str | None = Header(default=None)):
    require_auth_header(authorization)
    with get_conn() as conn:
        row = conn.execute(
            """INSERT INTO items (name, base_unit_id, case_size, allow_partials, par_level, low_threshold, default_location_id, active)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
               RETURNING id""",
            (req.name, str(req.base_unit_id), req.case_size, req.allow_partials, req.par_level, req.low_threshold,
             str(req.default_location_id) if req.default_location_id else None, req.active),
        ).fetchone()
        conn.commit()
    return {"id": str(row[0])}

@app.put("/items/{item_id}")
def update_item(item_id: UUID, req: ItemUpdate, authorization: str | None = Header(default=None)):
    require_auth_header(authorization)
    with get_conn() as conn:
        conn.execute(
            """UPDATE items SET name=%s, base_unit_id=%s, case_size=%s, allow_partials=%s, par_level=%s, low_threshold=%s,
               default_location_id=%s, active=%s, updated_at=now()
               WHERE id=%s""",
            (req.name, str(req.base_unit_id), req.case_size, req.allow_partials, req.par_level, req.low_threshold,
             str(req.default_location_id) if req.default_location_id else None, req.active, str(item_id)),
        )
        conn.commit()
    return {"ok": True}

@app.post("/sync/push")
def sync_push(req: SyncPushReq, authorization: str | None = Header(default=None)):
    require_auth_header(authorization)
    inserted = 0
    with get_conn() as conn:
        for e in req.events:
            try:
                conn.execute(
                    """INSERT INTO inventory_events
                       (event_type, item_id, delta_base_units, notes, photo_url, ref_type, ref_id, client_event_id, device_id)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (
                        e.event_type,
                        str(e.item_id),
                        e.delta_base_units,
                        e.notes,
                        e.photo_url,
                        e.ref_type,
                        str(e.ref_id) if e.ref_id else None,
                        str(e.client_event_id),
                        req.device_id,
                    ),
                )
                inserted += 1
            except Exception:
                conn.rollback()
                continue
        conn.commit()
    return {"inserted": inserted}

@app.get("/sync/pull")
def sync_pull(since: str = "1970-01-01T00:00:00Z", authorization: str | None = Header(default=None)):
    require_auth_header(authorization)
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT id, event_type, item_id, delta_base_units, notes, photo_url, ref_type, ref_id, client_event_id, device_id, created_at
               FROM inventory_events
               WHERE created_at > %s
               ORDER BY created_at ASC""",
            (since,),
        ).fetchall()
    events = []
    for r in rows:
        events.append({
            "id": str(r[0]),
            "event_type": r[1],
            "item_id": str(r[2]),
            "delta_base_units": float(r[3]),
            "notes": r[4],
            "photo_url": r[5],
            "ref_type": r[6],
            "ref_id": str(r[7]) if r[7] else None,
            "client_event_id": str(r[8]),
            "device_id": r[9],
            "created_at": r[10].isoformat(),
        })
    return {"events": events}

@app.get("/inventory/onhand")
def get_onhand(authorization: str | None = Header(default=None)):
    """Returns on-hand totals per item (sum of deltas)."""
    require_auth_header(authorization)
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT item_id, COALESCE(SUM(delta_base_units),0) AS onhand
               FROM inventory_events
               GROUP BY item_id"""
        ).fetchall()
    return {str(r[0]): float(r[1]) for r in rows}
