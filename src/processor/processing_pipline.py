from src.processor.analyze_trends import analyze_trends
from src.processor.storage import save_analysis
from src.processor.loader import load_latest_csv, load_previous_csv
from src.utils.logger import setup_logger
import time

logger = setup_logger("processor")

def run_preprocess(topic: str = "machine learning"):
    """
    Load latest and previous CSV data, analyze trends, and save analysis results.
    Raises exceptions if critical steps fail.
    """
    start_time = time.time()
    logger.info(f"Processing started for topic '{topic}'")

    try:
        current_data = load_latest_csv(topic)
        previous_data = load_previous_csv(topic)

        if current_data.empty:
            raise ValueError(f"No current data available for topic '{topic}'")

        if previous_data is None:
            logger.info(f"No previous data found for '{topic}', analysis will run without comparison.")

        analysis = analyze_trends(current_data, previous_data, topic=topic)
        save_path = save_analysis(analysis, topic)

        elapsed = time.time() - start_time
        logger.info(f"Processing completed successfully in {elapsed:.2f}s, saved to '{save_path}'")

        return save_path

    except Exception as e:
        logger.exception(f"Processing pipeline failed for topic '{topic}': {e}")
        raise
