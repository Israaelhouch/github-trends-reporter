import logging

from .mailer import email_configured, send_email
from .templates import generate_email_subject, generate_html, generate_text

logger = logging.getLogger(__name__)


def run_notifier(results: dict) -> bool:
    """Email the report if email is configured. Returns True when an email was sent."""
    if not email_configured():
        logger.info("Email not configured - skipping notification.")
        return False
    send_email(generate_email_subject(results), generate_text(results), generate_html(results))
    return True
