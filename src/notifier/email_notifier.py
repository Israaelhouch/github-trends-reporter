import yagmail
from src.utils.logger import setup_logger
from config import EMAIL_USER, EMAIL_PASS, EMAIL_RECEIVER

logger = setup_logger("notifier")

def send_email(subject: str, body: str, html: bool = True):
    """
    Send an email in GitHub Actions without ~/.yagmail dependency.
    """
    try:
        yag = yagmail.SMTP(
            user=EMAIL_USER,
            password=EMAIL_PASS,
            host='smtp.gmail.com',  # explicit SMTP host
            port=587,
            smtp_starttls=True,
            smtp_ssl=False
        )

        contents = [body] if not html else [yagmail.inline(body)]

        yag.send(
            to=EMAIL_RECEIVER,
            subject=subject,
            contents=contents
        )

        logger.info(f"Email sent successfully to {EMAIL_RECEIVER}")

    except Exception as e:
        logger.exception(f"Failed to send email: {e}")
        raise
