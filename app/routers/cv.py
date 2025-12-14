from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..deps import get_current_user

router = APIRouter()

class CVIn(BaseModel):
    full_name: str = ""
    title: str = ""
    summary: str = ""

@router.post("/generate")
def generate_cv(payload: CVIn, user=Depends(get_current_user)):
    # Placeholder: this endpoint can later generate a DOCX via templates.
    return {"ok": True, "message": "Génération CV (placeholder).", "data": payload.model_dump()}
