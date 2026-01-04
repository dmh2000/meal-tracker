import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from flask import request, jsonify, g

from database import query_db, execute_db

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"


def hash_password(password: str) -> tuple[bytes, bytes]:
    """Hash a password with bcrypt and return (hash, salt)."""
    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)
    return password_hash, salt


def verify_password(password: str, password_hash: bytes) -> bool:
    """Verify a password against a hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash)


def create_session_token(user_id: int, remember_me: bool = False) -> str:
    """Create a session token and store it in the database."""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    if remember_me:
        expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    execute_db(
        "INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)",
        (user_id, token_hash, expires_at.isoformat())
    )

    return token


def validate_session_token(token: str) -> dict | None:
    """Validate a session token and return user info if valid."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    session = query_db(
        """
        SELECT s.user_id, s.expires_at, u.username
        FROM sessions s
        JOIN users u ON u.id = s.user_id
        WHERE s.token = ?
        """,
        (token_hash,),
        one=True
    )

    if not session:
        return None

    expires_at = datetime.fromisoformat(session["expires_at"])
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if datetime.now(timezone.utc) > expires_at:
        execute_db("DELETE FROM sessions WHERE token = ?", (token_hash,))
        return None

    return {"id": session["user_id"], "username": session["username"]}


def invalidate_session_token(token: str) -> bool:
    """Invalidate a session token."""
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    execute_db("DELETE FROM sessions WHERE token = ?", (token_hash,))
    return True


def login_required(f):
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get("session_token")

        if not token:
            return jsonify({"error": "Authentication required"}), 401

        user = validate_session_token(token)
        if not user:
            return jsonify({"error": "Invalid or expired session"}), 401

        g.user = user
        return f(*args, **kwargs)

    return decorated_function
