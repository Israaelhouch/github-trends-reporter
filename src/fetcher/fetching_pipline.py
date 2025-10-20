import time
from .github_api import fetch_trending_repos
from src.db.repo_db import GitHubDB
from src.utils.logger import setup_logger

logger = setup_logger("fetcher")

def run_fetch(topic: str = None, top_n: int = 200, db=None):
    """
    Fetch trending repositories for a given topic and save them in PostgreSQL.
    Raises an exception if fetching or saving fails.
    """
    start_time = time.time()
    logger.info("Starting fetching pipeline...")

    try:
        logger.info(f"Fetching top {top_n} repositories for topic: '{topic}'")
        repos = fetch_trending_repos(topic=topic, top_n=top_n)

        if repos.empty:
            raise ValueError(f"No repositories fetched for topic '{topic}'")

        fetched_at = db.save_repos(repos, topic)
        logger.info(f"Data saved at {fetched_at}")

        elapsed = time.time() - start_time
        logger.info(f"Fetching pipeline completed successfully in {elapsed:.2f}s")

    except Exception as e:
        logger.exception(f"Fetching pipeline failed for topic '{topic}': {e}")
        raise
