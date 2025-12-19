import os
from datetime import datetime, timedelta, timezone

import jwt


def create_access_token(subject: str, expires_minutes: int = 60 * 24) -> str:
    secret = os.getenv("JWT_SECRET", "dev-secret")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "exp": now + timedelta(minutes=expires_minutes),
        "iat": now,
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    secret = os.getenv("JWT_SECRET", "dev-secret")
    return jwt.decode(token, secret, algorithms=["HS256"])
