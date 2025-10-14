
from .github_api import fetch_trending_repos
from .data_saver import save_raw_csv
from src.utils.logger import setup_logger

logger = setup_logger("fetcher")

def run_fetch(topic: str = None, top_n: int = 200):
    logger.info("Starting fetching pipeline...")
    try:
        logger.info(f"Fetching topic: {topic}")
        repos = fetch_trending_repos(topic=topic, top_n=top_n)
        save_raw_csv(repos, topic)
    except Exception as e:
        logger.exception(f"Error processing topic '{topic}': {e}")



from .github_api import fetch_trending_repos
from .data_saver import save_raw_csv
from src.utils.logger import setup_logger
import time

logger = setup_logger("fetcher")

def run_fetch(topic: str = None, top_n: int = 200):
    """
    Fetch trending repositories for a given topic and save as CSV.
    Raises an exception if fetching or saving fails.
    """
    start_time = time.time()
    logger.info("Starting fetching pipeline...")

    try:
        logger.info(f"Fetching top {top_n} repositories for topic: '{topic}'")
        repos = fetch_trending_repos(topic=topic, top_n=top_n)

        if repos.empty:
            raise ValueError(f"No repositories fetched for topic '{topic}'")

        save_raw_csv(repos, topic)
        elapsed = time.time() - start_time
        logger.info(f"Fetching pipeline completed successfully in {elapsed:.2f}s")

    except Exception as e:
        logger.exception(f"Fetching pipeline failed for topic '{topic}': {e}")
        raise 
