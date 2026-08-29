import hashlib
import secrets
from datetime import datetime, timedelta

import bcrypt
from jose import jwt

from app.core.config import settings


def get_password_hash(password: str) -> str:
    """Hashes a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hash"""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def create_access_token(user_id: int) -> str:
    """Creates a short-lived JWT (15 mins)"""
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"sub": str(user_id), "type": "access", "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token_value() -> str:
    """Creates a long-lived, opaque random string"""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hashes the refresh token using SHA-256"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """Checks if the raw token matches the hash in the DB"""
    return hash_token(token) == token_hash
