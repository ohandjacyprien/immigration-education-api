from fastapi import FastAPI, Body, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone

from .routers import auth, cv, payments, webhooks, premium
from .db_sqlite import init_db, execute
from .deps import get_current_user

app = FastAPI(title="EduQuébec API", version="0.3.0")

@app.on_event("startup")
def _startup():
    init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(cv.router, prefix="/cv", tags=["cv"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
app.include_router(premium.router, prefix="/premium", tags=["premium"])

@app.get("/health")
def health():
    return {"ok": True, "ts": datetime.now(timezone.utc).isoformat()}

@app.post("/contact")
def contact(payload: dict = Body(...)):
    name = str(payload.get("name","")).strip() or str(payload.get("cName","")).strip()
    email = str(payload.get("email","")).strip() or str(payload.get("cEmail","")).strip()
    message = str(payload.get("message","")).strip() or str(payload.get("cMsg","")).strip()
    if not name or not email or not message:
        raise HTTPException(status_code=400, detail="Champs requis: name, email, message.")
    now = datetime.now(timezone.utc).isoformat()
    execute("INSERT INTO contact_messages(name,email,message,created_at) VALUES (?,?,?,?)",
            (name, email, message, now))
    return {"ok": True}
