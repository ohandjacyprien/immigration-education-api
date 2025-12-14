import smtplib
from email.message import EmailMessage
from .settings import settings

def send_email(to_email: str, subject: str, html: str, text: str = "") -> None:
    """Send an email using SMTP settings. In dev, if SMTP is not configured, it prints to console."""
    if not settings.SMTP_HOST:
        # Dev fallback
        print("=== EMAIL (dev fallback) ===")
        print("To:", to_email)
        print("Subject:", subject)
        print(text or html)
        print("============================")
        return

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    if text:
        msg.set_content(text)
    else:
        msg.set_content("Votre client email ne supporte pas le HTML.")
    msg.add_alternative(html, subtype="html")

    if settings.SMTP_USE_TLS:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as s:
            s.starttls()
            if settings.SMTP_USER:
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.send_message(msg)
    else:
        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as s:
            if settings.SMTP_USER:
                s.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            s.send_message(msg)
