import logging
import smtplib
from email.message import EmailMessage

from src import config

logger = logging.getLogger(__name__)


class EmailError(RuntimeError):
    pass


def email_configured() -> bool:
    return bool(config.EMAIL_USER and config.EMAIL_PASS and config.EMAIL_RECEIVER)


def send_email(subject: str, text: str, html: str | None = None) -> None:
    """Send a multipart (plain text + HTML) email over STARTTLS."""
    if not email_configured():
        raise ValueError("Email is not configured: set EMAIL_USER, EMAIL_PASS and EMAIL_TO.")

    msg = EmailMessage()
    msg["From"] = config.EMAIL_USER
    msg["To"] = config.EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.set_content(text)
    if html:
        msg.add_alternative(html, subtype="html")

    try:
        with smtplib.SMTP(config.EMAIL_SMTP_SERVER, config.EMAIL_SMTP_PORT, timeout=30) as server:
            server.starttls()
            try:
                server.login(config.EMAIL_USER, config.EMAIL_PASS)
            except (smtplib.SMTPAuthenticationError, smtplib.SMTPServerDisconnected) as exc:
                raise EmailError(
                    f"SMTP login failed for {config.EMAIL_USER}. Check EMAIL_USER and EMAIL_PASS - for Gmail, "
                    "EMAIL_PASS must be a valid App Password (https://myaccount.google.com/apppasswords)."
                ) from exc
            server.send_message(msg)
    except (smtplib.SMTPException, OSError) as exc:
        if isinstance(exc, EmailError):
            raise
        raise EmailError(f"Could not send email via {config.EMAIL_SMTP_SERVER}: {exc}") from exc
    logger.info("Email sent to %s", config.EMAIL_RECEIVER)
