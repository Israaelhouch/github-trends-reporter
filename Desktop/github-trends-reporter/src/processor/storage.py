import json
from datetime import datetime
import os
from utils.logger import setup_logger

logger = setup_logger("processor")

from config import DATA_OUTPUT_DIR

os.makedirs(DATA_OUTPUT_DIR, exist_ok=True)

def save_analysis(data, topic: str = "general") :
    """
    Save analysis results to a JSON file.
    - Includes topic name and timestamp in filename.
    - Returns the full path to the saved file or None if failed.
    """
    try:
        safe_topic = topic.replace(" ", "_")
        filename = f"analysis_{safe_topic}_{datetime.now().strftime('%Y-%m-%d')}.json"
        filepath = os.path.join(DATA_OUTPUT_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        
        logger.info(f"Trend analysis for '{topic}' saved at: {filepath}")

    except Exception as e:
        logger.exception(f"Failed to save analysis for '{topic}': {e}")
