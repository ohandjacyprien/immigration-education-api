from fastapi import Header, HTTPException, Depends
import jwt
from typing import Optional, Dict, Any
from .settings import settings
from .db_sqlite import fetch_one

def get_current_user(authorization: Optional[str] = Header(default=None)) -> Dict[str, Any]:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Non authentifié.")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(status_code=401, detail="Token invalide.")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token invalide.")
    user = fetch_one("SELECT id,email,created_at FROM users WHERE email=?", (email.lower().strip(),))
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable.")
    return user

def require_premium(user=Depends(get_current_user)) -> Dict[str, Any]:
    sub = fetch_one("SELECT status FROM subscriptions WHERE user_id=?", (user["id"],))
    if not sub or sub["status"] != "active":
        raise HTTPException(status_code=403, detail="Accès premium requis.")
    return user
