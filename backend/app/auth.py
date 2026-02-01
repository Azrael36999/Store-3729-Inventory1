import os
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
from .db import get_conn

JWT_SECRET = os.environ.get("JWT_SECRET", "change-me")
JWT_ALG = "HS256"
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_token() -> str:
    exp = datetime.utcnow() + timedelta(days=7)
    return jwt.encode({"exp": exp}, JWT_SECRET, algorithm=JWT_ALG)

def require_auth_header(authorization: str | None) -> None:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401, "Unauthorized")
    token = authorization.split(" ", 1)[1]
    try:
        jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except Exception:
        raise HTTPException(401, "Unauthorized")

def verify_login(username: str, password: str) -> str:
    with get_conn() as conn:
        row = conn.execute("SELECT username, password_hash FROM auth_secrets WHERE id=1").fetchone()
        if not row:
            raise HTTPException(500, "Auth not initialized")
        db_user, db_hash = row
        if username != db_user or not pwd.verify(password, db_hash):
            raise HTTPException(401, "Invalid login")
    return create_token()

def init_shared_login_if_missing() -> None:
    """Create the shared login row if missing, using INIT_USERNAME/INIT_PASSWORD env vars."""
    init_user = os.environ.get("INIT_USERNAME")
    init_pass = os.environ.get("INIT_PASSWORD")
    if not init_user or not init_pass:
        # Not fatal; allows initializing later via SQL
        return
    with get_conn() as conn:
        row = conn.execute("SELECT username FROM auth_secrets WHERE id=1").fetchone()
        if row:
            return
        conn.execute(
            "INSERT INTO auth_secrets (id, username, password_hash) VALUES (1, %s, %s)",
            (init_user, pwd.hash(init_pass)),
        )
        conn.commit()
