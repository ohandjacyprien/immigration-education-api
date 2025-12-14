from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext
from .settings import settings

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    return pwd.hash(p)

def verify_password(p: str, hashed: str) -> bool:
    return pwd.verify(p, hashed)

def create_access_token(sub: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRES_MIN)
    return jwt.encode({"sub": sub, "exp": exp}, settings.JWT_SECRET, algorithm="HS256")
