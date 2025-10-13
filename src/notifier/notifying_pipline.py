import json
import os
from config import DATA_OUTPUT_DIR
from src.utils.logger import setup_logger
from .templates import generate_email_subject, generate_email_body
from .email_notifier import send_email
from datetime import datetime

logger = setup_logger("notifier")

def run_notifier(topic: str ="machine learning", html: bool =True):
    """Find latest analysis and send it by email"""

    safe_topic = topic.replace(" ", "_")
    filename = f"analysis_{safe_topic}_{datetime.now().strftime('%Y_%m_%d')}.json"
    analysis_file =os.path.join(DATA_OUTPUT_DIR, filename)

    if not os.path.exists(analysis_file):
            logger.error(f"Results file not found: {analysis_file}")
            return 

    logger.info(f"Preparing email from: {analysis_file}")

    with open(analysis_file, "r", encoding="utf-8") as f:
        results = json.load(f)

    subject = generate_email_subject(topic)
    body = generate_email_body(results, html=True)
    send_email(subject, body)
