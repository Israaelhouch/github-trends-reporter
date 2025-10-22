from src.processor.analyze_trends import analyze_trends
from src.processor.storage import save_analysis
from src.db.repo_db import GitHubDB
from src.utils.logger import setup_logger
import time
import pandas as pd

logger = setup_logger("processor")

def run_preprocess(topic: str = "machine learning", db=None):
    """
    Load the latest and previous fetches from the database,
    analyze trends, and save analysis results.
    """
    start_time = time.time()
    logger.info(f"Processing started for topic '{topic}'")

    try:
        # Load latest fetches
        current_data, previous_data = db.load_latest_fetches(topic)

        if current_data is None or current_data.empty:
            raise ValueError(f"No current data available for topic '{topic}'")

        if previous_data is None or previous_data.empty:
            logger.info(f"No previous data found for '{topic}', analysis will run without comparison.")
            previous_data = pd.DataFrame()  # Ensure analyze_trends can handle empty previous_data

        # Run analysis
        analysis = analyze_trends(current_data, previous_data, topic=topic)

        # Save results
        save_path = save_analysis(analysis, topic)

        elapsed = time.time() - start_time
        logger.info(f"Processing completed successfully in {elapsed:.2f}s, saved to '{save_path}'")

        return save_path

    except Exception as e:
        logger.exception(f"Processing pipeline failed for topic '{topic}': {e}")
        raise
