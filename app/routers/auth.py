from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import datetime, timezone, timedelta
import secrets

from ..security import hash_password, verify_password, create_access_token
from ..db_sqlite import fetch_one, execute
from ..settings import settings
from ..emailer import send_email

router = APIRouter()

class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class ResendIn(BaseModel):
    email: EmailStr

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _make_token() -> str:
    return secrets.token_urlsafe(32)

def _verify_link(token: str) -> str:
    # Frontend page that calls the API
    base = settings.FRONTEND_BASE_URL.rstrip("/")
    return f"{base}/verify.html?token={token}"

@router.post("/register")
def register(payload: RegisterIn):
    email = payload.email.lower().strip()
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="Mot de passe trop court (8 caractères minimum).")

    existing = fetch_one("SELECT id, is_active, email_verified FROM users WHERE email=?", (email,))
    if existing and int(existing.get("email_verified", 0)) == 1:
        raise HTTPException(status_code=409, detail="Utilisateur déjà enregistré.")

    token = _make_token()
    expires = (datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFY_EXPIRES_MIN)).isoformat()

    if existing:
        # user exists but not verified yet -> refresh token
        execute("UPDATE users SET password_hash=?, verify_token=?, verify_token_expires_at=?, is_active=0, email_verified=0 WHERE email=?",
                (hash_password(payload.password), token, expires, email))
    else:
        execute(
            "INSERT INTO users(email,password_hash,created_at,is_active,email_verified,verify_token,verify_token_expires_at) VALUES (?,?,?,?,?,?,?)",
            (email, hash_password(payload.password), _now_iso(), 0, 0, token, expires),
        )

    link = _verify_link(token)
    subject = "Confirmez votre email — EduQuébec"
    html = f"""
    <p>Bonjour,</p>
    <p>Merci d’avoir créé votre compte sur <strong>EduQuébec</strong>.</p>
    <p>Pour activer votre compte, confirmez votre adresse email en cliquant sur ce lien :</p>
    <p><a href="{link}">Activer mon compte</a></p>
    <p>Ce lien expire dans {settings.EMAIL_VERIFY_EXPIRES_MIN} minutes.</p>
    <p>Si vous n’êtes pas à l’origine de cette demande, ignorez ce message.</p>
    """
    text = f"Activez votre compte EduQuébec: {link} (expire dans {settings.EMAIL_VERIFY_EXPIRES_MIN} minutes)."
    send_email(email, subject, html, text=text)

    return {"ok": True, "message": "Email de confirmation envoyé. Veuillez activer votre compte."}

@router.get("/verify")
def verify(token: str):
    token = token.strip()
    u = fetch_one("SELECT id, verify_token_expires_at FROM users WHERE verify_token=?", (token,))
    if not u:
        raise HTTPException(status_code=400, detail="Lien invalide ou expiré.")
    exp = u.get("verify_token_expires_at")
    if exp:
        try:
            exp_dt = datetime.fromisoformat(exp.replace("Z","+00:00"))
        except Exception:
            exp_dt = None
        if exp_dt and exp_dt < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Lien expiré. Demandez un nouvel email.")
    execute("UPDATE users SET is_active=1, email_verified=1, verify_token=NULL, verify_token_expires_at=NULL WHERE id=?",
            (u["id"],))
    return {"ok": True, "message": "Compte activé. Vous pouvez vous connecter."}

@router.post("/resend-verification")
def resend(payload: ResendIn):
    email = payload.email.lower().strip()
    u = fetch_one("SELECT id, email_verified FROM users WHERE email=?", (email,))
    if not u:
        # Do not leak account existence
        return {"ok": True, "message": "Si un compte existe, un email a été envoyé."}
    if int(u.get("email_verified", 0)) == 1:
        return {"ok": True, "message": "Compte déjà activé."}

    token = _make_token()
    expires = (datetime.now(timezone.utc) + timedelta(minutes=settings.EMAIL_VERIFY_EXPIRES_MIN)).isoformat()
    execute("UPDATE users SET verify_token=?, verify_token_expires_at=? WHERE id=?", (token, expires, u["id"]))

    link = _verify_link(token)
    subject = "Nouveau lien de confirmation — EduQuébec"
    html = f"""<p>Bonjour,</p><p>Voici votre nouveau lien d’activation :</p><p><a href="{link}">Activer mon compte</a></p>"""
    text = f"Nouveau lien d’activation EduQuébec: {link}"
    send_email(email, subject, html, text=text)

    return {"ok": True, "message": "Email envoyé."}

@router.post("/login")
def login(payload: LoginIn):
    email = payload.email.lower().strip()
    u = fetch_one("SELECT id,email,password_hash,is_active,email_verified FROM users WHERE email=?", (email,))
    if not u or not verify_password(payload.password, u["password_hash"]):
        raise HTTPException(status_code=401, detail="Identifiants invalides.")
    if int(u.get("email_verified", 0)) != 1 or int(u.get("is_active", 0)) != 1:
        raise HTTPException(status_code=403, detail="Compte non activé. Vérifiez votre email.")
    return {"access_token": create_access_token(email), "token_type": "bearer"}
