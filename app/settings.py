from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Object storage (S3 / Cloudflare R2)
    S3_ENDPOINT_URL: str = ""  # e.g. https://<accountid>.r2.cloudflarestorage.com
    S3_ACCESS_KEY_ID: str = ""
    S3_SECRET_ACCESS_KEY: str = ""
    S3_REGION: str = "auto"  # R2 uses 'auto'
    S3_BUCKET: str = ""
    S3_PREFIX: str = "premium/"  # folder prefix in bucket
    S3_SIGNED_URL_EXPIRES_SEC: int = 300

    APP_ENV: str = "dev"
    JWT_SECRET: str = "change-me"
    JWT_EXPIRES_MIN: int = 120
    STRIPE_SECRET_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""
    FRONTEND_BASE_URL: str = "http://127.0.0.1:5500"

    # Email (SMTP)
    SMTP_HOST: str = ""  # e.g. smtp.gmail.com
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "EduQuébec <no-reply@eduquebec.ca>"
    SMTP_USE_TLS: bool = True

    EMAIL_VERIFY_EXPIRES_MIN: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
