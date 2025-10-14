import yagmail
from src.utils.logger import setup_logger
from config import EMAIL_USER, EMAIL_PASS, EMAIL_RECEIVER

logger = setup_logger("notifier")

def send_email(subject: str, body: str, html: bool = True):
    """
    Send an email notification with GitHub trend results.
    Works both locally and in CI (GitHub Actions) — no ~/.yagmail file needed.
    """
    try:
        yag = yagmail.SMTP(
            user=EMAIL_USER,
            password=EMAIL_PASS,
            oauth2_file=None  # disables searching for ~/.yagmail
        )

        contents = [body] if not html else [body]

        yag.send(
            to=EMAIL_RECEIVER,
            subject=subject,
            contents=contents
        )

        logger.info(f"Email sent successfully to {EMAIL_RECEIVER}")

    except Exception as e:
        logger.error(f"Failed to send email: {e}", exc_info=True)
        raise
