import os
import csv
from config import DATA_RAW_DIR
from src.utils.logger import setup_logger
from datetime import datetime

logger = setup_logger("fetcher")

os.makedirs(DATA_RAW_DIR, exist_ok=True)

def save_raw_csv(df, topic: str):
    """Save list of repos as CSV in raw folder"""
    filename = f"{DATA_RAW_DIR}/github_trends_{topic.replace(' ', '_')}_{datetime.utcnow().strftime('%Y_%m_%d')}.csv"
    df.to_csv(filename, index=False)
    logger.info(f"Saved {len(df)} repositories to '{filename}'")
