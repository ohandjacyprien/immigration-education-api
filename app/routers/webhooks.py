from fastapi import APIRouter, Request, HTTPException
from datetime import datetime, timezone
import stripe

from ..settings import settings
from ..db_sqlite import fetch_one, execute

router = APIRouter()

@router.post("/stripe")
async def stripe_webhook(request: Request):
    if not settings.STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=500, detail="Stripe webhook non configuré.")
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Signature invalide.")

    if event["type"] == "checkout.session.completed":
        sess = event["data"]["object"]
        email = (sess.get("metadata") or {}).get("email")
        if email:
            user = fetch_one("SELECT id FROM users WHERE email=?", (email.lower().strip(),))
            if user:
                now = datetime.now(timezone.utc).isoformat()
                execute("INSERT INTO subscriptions(user_id,status,provider,provider_ref,updated_at) VALUES (?,?,?,?,?)",
                        (user["id"], "active", "stripe", sess.get("id"), now))
    return {"ok": True}
