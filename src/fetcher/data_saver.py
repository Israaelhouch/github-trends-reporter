import os
from datetime import datetime
from config import DATA_RAW_DIR
from src.utils.logger import setup_logger
import pandas as pd

logger = setup_logger("fetcher")

os.makedirs(DATA_RAW_DIR, exist_ok=True)

def save_raw_csv(df: pd.DataFrame, topic: str):
    """
    Save list of repositories as CSV in the raw data folder.
    Raises an exception if saving fails or DataFrame is empty.
    """
    if df.empty:
        raise ValueError(f"No data to save for topic '{topic}'")

    safe_topic = topic.replace(" ", "_").lower()
    filename = os.path.join(
        DATA_RAW_DIR,
        f"github_trends_{safe_topic}_{datetime.utcnow().strftime('%Y_%m_%d')}.csv"
    )

    try:
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(df)} repositories to '{filename}'")
        return filename
    except Exception as e:
        logger.exception(f"Failed to save CSV for topic '{topic}': {e}")
        raise
