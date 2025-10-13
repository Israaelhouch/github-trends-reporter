import os
import csv
import json
from config import DATA_RAW_DIR, DATA_OUTPUT_DIR
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger("fetcher")

os.makedirs(DATA_RAW_DIR, exist_ok=True)
os.makedirs(DATA_OUTPUT_DIR, exist_ok=True)

def save_json(data, name: str):
    """Save analysis or raw data as JSON"""
    if not data:
        logger.warning("No data to save in JSON.")
        return
    filepath = os.path.join(DATA_OUTPUT_DIR, f"{name}_{datetime.utcnow().strftime('%Y_%m_%d')}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    logger.info(f"Saved JSON file: {filepath}")
