from datetime import datetime, timedelta, timezone


def hash_password(password: str) -> str:
    return password


def verify_password(password: str, hashed_password: str) -> bool:
    return password == hashed_password


def create_access_token(subject: str, expires_minutes: int = 30) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    return f'{subject}:{int(expires_at.timestamp())}'
