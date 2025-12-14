# Backend EduQuébec (FastAPI)

## Installation
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## Docs
- http://127.0.0.1:8000/docs

## Endpoints ()
- POST /auth/register
- POST /auth/login
- POST /cv/export/pdf
- POST /cv/export/docx
- POST /payments/checkout
- POST /webhooks/stripe


## Connexion Front
- Lancez le back : `uvicorn app.main:app --reload --port 8000`
- Lancez le front : `python -m http.server 5500` à la racine du projet
- Le front appelle l'API via `window.EDUQ.API_BASE_URL` (js/config.js)


## Endpoints supplémentaires
- GET /me
- GET /premium/status
- GET /premium/resources (premium requis)
- GET /orders/ (historique commandes)

## Base de données
- Fichier SQLite: `backend/data.sqlite3`

- GET /premium/download/{resource_id} (premium requis, téléchargement)


## Stockage cloud (S3 / Cloudflare R2) + URL signées

### Configuration
Dans `.env` :
- `S3_ENDPOINT_URL` (R2: `https://<accountid>.r2.cloudflarestorage.com`)
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `S3_REGION` (R2: `auto`)
- `S3_BUCKET`
- `S3_PREFIX` (ex: `premium/`)

### Upload des fichiers premium
Chargez vos fichiers dans le bucket sous le préfixe `premium/` :
- `premium/modele_cv_quebec.docx`
- `premium/lettre_css.docx`
- `premium/plan_tecfee_30j.pdf`
- `premium/checklist_dossier.pdf`

### Endpoints
- `GET /premium/signed-url/{resource_id}` → retourne une URL signée (si S3/R2 configuré)
- `GET /premium/download/{resource_id}` → fallback local (dev)


## Ressources TECFÉE (Premium)
Les PDF TECFÉE sont servis via les endpoints premium (/premium/signed-url ou /premium/download) et ne sont plus accessibles en statique.
