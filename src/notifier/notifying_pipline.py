import json
import os
import time
from datetime import datetime
from config import DATA_OUTPUT_DIR
from src.utils.logger import setup_logger
from .templates import generate_email_subject, generate_email_body
from .find_file import find_latest_analysis_file
from .email_notifier import send_email

logger = setup_logger("notifier")

def run_notifier(topic: str = "machine learning", html: bool = True):
    """
    Find latest analysis results and send them via email.
    """
    start_time = time.time()
    logger.info(f"Starting notifier for topic '{topic}'")

    try:
        analysis_file = find_latest_analysis_file(topic)
        if not analysis_file:
            logger.warning(f"No analysis results available for '{topic}', skipping email.")
            return

        # Load the analysis JSON
        with open(analysis_file, "r", encoding="utf-8") as f:
            results = json.load(f)

        subject = generate_email_subject(topic)
        body = generate_email_body(results, html=html)

        # Send email
        send_email(subject, body, html=html)
        elapsed = time.time() - start_time
        logger.info(f"Email successfully sent for '{topic}' in {elapsed:.2f}s")

    except Exception as e:
        logger.exception(f"Failed to send email for '{topic}': {e}")
        raise  
