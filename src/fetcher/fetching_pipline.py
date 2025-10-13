
from .github_api import fetch_trending_repos
from .data_saver import save_raw_csv
from utils.logger import setup_logger

logger = setup_logger("fetcher")

def run_fetch(language: str = None, top_n: int = 200):
    logger.info("Starting fetching pipeline...")
    
    repos = fetch_trending_repos(language=language,top_n=top_n)
    if not repos:
        logger.warning("No repositories fetched.")
        return
    save_raw_csv(repos, "github_trending")
    logger.info("Fetching pipeline completed successfully.")

