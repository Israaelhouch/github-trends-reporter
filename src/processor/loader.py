import os
import pandas as pd
from src.utils.logger import setup_logger
from config import DATA_RAW_DIR

logger = setup_logger("processor")

def load_latest_csv(topic: str) -> pd.DataFrame:
    """
    Load the most recent CSV for a given topic using file modification time.
    Returns empty DataFrame if no CSV exists.
    """
    try:
        if not os.path.exists(DATA_RAW_DIR):
            logger.warning(f"Data folder '{DATA_RAW_DIR}' does not exist.")
            return pd.DataFrame()

        files = [
            os.path.join(DATA_RAW_DIR, f)
            for f in os.listdir(DATA_RAW_DIR)
            if f.startswith(f"github_trends_{topic.replace(' ', '_')}")
        ]
        if not files:
            logger.warning(f"No CSV files found for topic '{topic}' in '{DATA_RAW_DIR}'")
            return pd.DataFrame()

        # Sort by modification time (latest last)
        latest_file = max(files, key=os.path.getmtime)
        logger.info(f"Loading latest CSV for topic '{topic}': {latest_file}")
        df = pd.read_csv(latest_file)
        if df.empty:
            logger.warning(f"Latest CSV '{latest_file}' is empty.")
        return df

    except Exception as e:
        logger.exception(f"Failed to load latest CSV for topic '{topic}': {e}")
        return pd.DataFrame()


def load_previous_csv(topic: str) -> pd.DataFrame | None:
    """
    Load the second-latest CSV for a given topic using modification time.
    Returns None if no previous file exists.
    """
    try:
        if not os.path.exists(DATA_RAW_DIR):
            logger.warning(f"Data folder '{DATA_RAW_DIR}' does not exist.")
            return None

        files = [
            os.path.join(DATA_RAW_DIR, f)
            for f in os.listdir(DATA_RAW_DIR)
            if f.startswith(f"github_trends_{topic.replace(' ', '_')}")
        ]
        if len(files) < 2:
            logger.info(f"Not enough data to load previous CSV for topic '{topic}'")
            return None

        # Sort by modification time
        files_sorted = sorted(files, key=os.path.getmtime)
        prev_file = files_sorted[-2]

        logger.info(f"Loading previous CSV for topic '{topic}': {prev_file}")
        df = pd.read_csv(prev_file)
        if df.empty:
            logger.warning(f"Previous CSV '{prev_file}' is empty.")
        return df

    except Exception as e:
        logger.exception(f"Failed to load previous CSV for topic '{topic}': {e}")
        return None
