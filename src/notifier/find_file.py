import os
from config import DATA_OUTPUT_DIR
from src.utils.logger import setup_logger

logger = setup_logger("notifier")


def find_latest_analysis_file(topic: str) -> str | None:
    """Find the most recent analysis JSON file for a given topic."""
    safe_topic = topic.replace(" ", "_")

    if not os.path.exists(DATA_OUTPUT_DIR):
        logger.error(f"Output directory not found: {DATA_OUTPUT_DIR}")
        return None

    files = [
        os.path.join(DATA_OUTPUT_DIR, f)
        for f in os.listdir(DATA_OUTPUT_DIR)
        if f.startswith(f"analysis_{safe_topic}_") and f.endswith(".json")
    ]

    if not files:
        logger.error(f"No analysis files found for topic '{topic}' in {DATA_OUTPUT_DIR}")
        return None

    latest_file = max(files, key=os.path.getmtime)
    logger.info(f"Latest analysis file selected: {latest_file}")
    return latest_file
