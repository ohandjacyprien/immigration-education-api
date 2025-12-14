from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timezone
import stripe

from ..settings import settings
from ..deps import get_current_user
from ..db_sqlite import execute

router = APIRouter()

class CheckoutIn(BaseModel):
    product: str  # 'premium'

@router.post("/checkout")
def create_checkout(payload: CheckoutIn, user=Depends(get_current_user)):
    if payload.product != "premium":
        raise HTTPException(status_code=400, detail="Produit invalide.")
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(status_code=500, detail="Stripe non configuré (STRIPE_SECRET_KEY).")

    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Simple fixed price (you can replace with Price IDs)
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{
            "price_data": {
                "currency": "cad",
                "product_data": {"name": "EduQuébec Premium"},
                "unit_amount": 1999,
            },
            "quantity": 1,
        }],
        success_url=f"{settings.FRONTEND_BASE_URL}/premium.html?success=1",
        cancel_url=f"{settings.FRONTEND_BASE_URL}/premium.html?canceled=1",
        metadata={"email": user["email"]},
    )
    return {"url": session.url}
