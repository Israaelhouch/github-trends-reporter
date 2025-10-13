import yagmail
from src.utils.logger import setup_logger
from config import EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT, EMAIL_USER, EMAIL_PASS, EMAIL_RECEIVER

logger = setup_logger("notifier")

def send_email(subject: str, body: str, html: bool=True):
    """
    Send an email notification with GitHub trend results.
    """
    try:
        yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)
        yag.send(
            to=EMAIL_RECEIVER,
            subject=subject,
            contents=[body] if not html else [yagmail.inline(body)]
        )
        logger.info(f"Email sent successfully to {EMAIL_RECEIVER}")
    except Exception as e:
        logger.exception(f"Failed to send email: {e}")
