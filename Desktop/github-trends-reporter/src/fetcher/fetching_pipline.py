
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
        return 
    return repos
