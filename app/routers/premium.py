from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path

from ..deps import require_premium, get_current_user
from ..storage import is_configured, presign_get_url, get_cfg
from ..db_sqlite import execute, fetch_one
from datetime import datetime, timezone

router = APIRouter()

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "premium"

# Catalog of premium-protected files
PREMIUM_FILES = {
    "tmpl-cv-quebec": {"filename": "modele_cv_quebec.docx", "title": "Modèle de CV (Québec)", "type": "docx"},
    "plan-tecfee-30j": {"filename": "plan_tecfee_30j.pdf", "title": "Plan TECFÉE — 30 jours", "type": "pdf"},
    "lettre-css": {"filename": "lettre_css.docx", "title": "Lettre — candidature CSS", "type": "docx"},
    "checklist-dossier": {"filename": "checklist_dossier.pdf", "title": "Checklist dossier", "type": "pdf"},
    # TECFÉE PDFs (added by you)
    "tecfee-compo": {"filename": "COMPO.pdf", "title": "COMPO — Grille / feuille de test", "type": "pdf"},
    "tecfee-doc-1": {"filename": "DOC-1.pdf", "title": "DOC-1 — Exercices préparatoires TECFÉE (Partie 1)", "type": "pdf"},
    "tecfee-doc-2": {"filename": "DOC-2.pdf", "title": "DOC-2 — Exercices préparatoires TECFÉE (Partie 2)", "type": "pdf"},
    "tecfee-doc-3": {"filename": "DOC-3 — Exercices préparatoires TECFÉE (Partie 3)".replace("—","-"), "title": "DOC-3 — Exercices préparatoires TECFÉE (Partie 3)", "type": "pdf"},
    "tecfee-doc-4": {"filename": "DOC-4.pdf", "title": "DOC-4 — Exercices préparatoires TECFÉE (Partie 4)", "type": "pdf"},
    "tecfee-doc-5": {"filename": "DOC-5.pdf", "title": "DOC-5 — Exercices préparatoires TECFÉE (Partie 5)", "type": "pdf"},
    "tecfee-doc-6": {"filename": "DOC-6.pdf", "title": "DOC-6 — Exercices préparatoires TECFÉE (Partie 6)", "type": "pdf"},
    "tecfee-doc-7": {"filename": "DOC-7.pdf", "title": "DOC-7 — Exercices préparatoires TECFÉE (Partie 7)", "type": "pdf"},
    "tecfee-doc-8": {"filename": "DOC-8.pdf", "title": "DOC-8 — Exercices préparatoires TECFÉE (Partie 8)", "type": "pdf"},
}

def _now_iso():
    return datetime.now(timezone.utc).isoformat()

@router.get("/status")
def status(user=Depends(get_current_user)):
    sub = fetch_one("SELECT status, updated_at FROM subscriptions WHERE user_id=?", (user["id"],))
    return {"status": (sub["status"] if sub else "inactive"), "updated_at": (sub["updated_at"] if sub else None)}

@router.get("/signed-url/{file_id}")
def signed_url(file_id: str, user=Depends(require_premium)):
    meta = PREMIUM_FILES.get(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Fichier introuvable.")
    filename = meta["filename"]

    execute("INSERT INTO premium_downloads(user_id,file_id,created_at) VALUES (?,?,?)", (user["id"], file_id, _now_iso()))

    # If object storage configured, presign; else serve from local assets
    if is_configured():
        cfg = get_cfg()
        key = f"{cfg.prefix}{filename}" if cfg.prefix else filename
        url = presign_get_url(key, download_name=filename)
        return {"url": url}

    path = ASSETS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=500, detail="Fichier non disponible côté serveur.")
    # frontend will call /download if local
    return {"url": f"/premium/download/{file_id}"}

@router.get("/download/{file_id}")
def download(file_id: str, user=Depends(require_premium)):
    meta = PREMIUM_FILES.get(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Fichier introuvable.")
    path = ASSETS_DIR / meta["filename"]
    if not path.exists():
        raise HTTPException(status_code=404, detail="Fichier manquant sur le serveur.")
    execute("INSERT INTO premium_downloads(user_id,file_id,created_at) VALUES (?,?,?)", (user["id"], file_id, _now_iso()))
    return FileResponse(path, filename=meta["filename"])
