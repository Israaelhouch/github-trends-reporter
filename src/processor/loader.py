import os
import pandas as pd
from src.utils.logger import setup_logger
from config import DATA_RAW_DIR
logger = setup_logger("processor")


def load_latest_csv(topic: str) -> pd.DataFrame | None:
    """
    Load the most recent CSV for a given topic using file modification time.
    Returns None if no CSV exists or loading fails.
    """
    try:
        if not os.path.exists(DATA_RAW_DIR):
            logger.warning(f"Data DATA_RAW_DIR '{DATA_RAW_DIR}' does not exist.")
            return None

        files = [
            os.path.join(DATA_RAW_DIR, f)
            for f in os.listdir(DATA_RAW_DIR)
            if f.startswith(f"github_trends_{topic.replace(' ', '_')}")
        ]
        if not files:
            logger.warning(f"No CSV files found for topic '{topic}' in '{DATA_RAW_DIR}'")
            return None

        # Sort by modification time (most recent last)
        files = sorted(files, key=os.path.getmtime)
        latest_file = files[-1]

        logger.info(f"Loading latest CSV for topic '{topic}': {latest_file}")
        df = pd.read_csv(latest_file)

        if df.empty:
            logger.warning(f"Latest CSV '{latest_file}' is empty.")
            return None

        return df

    except Exception as e:
        logger.exception(f"Failed to load latest CSV for topic '{topic}': {e}")
        return None



def load_previous_csv(topic: str) -> pd.DataFrame | None:
    """
    Load the second-latest CSV for a given topic.
    Returns None if no previous file exists or if loading fails.
    """
    try:
        if not os.path.exists(DATA_RAW_DIR):
            logger.warning(f"Data DATA_RAW_DIR '{DATA_RAW_DIR}' does not exist.")
            return None

        files = [
            f for f in os.listdir(DATA_RAW_DIR)
            if f.startswith(f"github_trends_{topic.replace(' ', '_')}")
        ]
        if len(files) < 2:
            logger.warning(f"Not enough data to load previous fetched data for topic '{topic}'")
            return None


        prev_file = sorted(files)[-2]
        filepath = os.path.join(DATA_RAW_DIR, prev_file)

        logger.info(f"Loading previous CSV for topic '{topic}': {filepath}")
        df = pd.read_csv(filepath)

        if df.empty:
            logger.warning(f"Previous CSV '{prev_file}' is empty.")
            return None

        return df

    except Exception as e:
        logger.exception(f"Failed to load previous CSV for topic '{topic}': {e}")
        return None
