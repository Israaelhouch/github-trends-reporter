import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config import EMAIL_USER, EMAIL_PASS, EMAIL_RECEIVER
from src.utils.logger import setup_logger

logger = setup_logger("notifier")

def send_email(subject: str, body: str, html: bool = True):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject

        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()

        logger.info(f"Email sent successfully to {EMAIL_RECEIVER}")

    except Exception as e:
        logger.exception(f"Failed to send email: {e}")
        raise
