import argparse
import os
from src.fetcher.fetching_pipline import run_fetch
from src.processor.processing_pipline import run_preprocess
from src.notifier.notifying_pipline import run_notifier
from src.db.repo_db import GitHubDB
from src.utils.logger import setup_logger
from config import TOPIC, TOP_N




logger = setup_logger("auto_notifier")

def main():
    parser = argparse.ArgumentParser(description="GitHub Trends Reporter")
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Topic to fetch trending GitHub repositories"
    )
    parser.add_argument(
        "--top_n",
        type=int,
        default=200,
        help="Number of repositories to fetch"
    )
    args = parser.parse_args()

    topic = args.topic or TOPIC
    top_n = args.top_n or TOP_N
    logger.info(f"Starting GitHub Trends Reporter pipeline for topic: '{topic}'")

    try:
        # Initialize DB
        db = GitHubDB()
        # Fetch stage
        run_fetch(topic=topic, top_n=top_n, db=db)
        logger.info("Fetching completed successfully.")

        # Process stage
        run_preprocess(topic=topic, db=db)
        logger.info("Processing completed successfully.")

        # Notify stage
        run_notifier(topic=topic)
        logger.info("Notification sent successfully.")
        
        db.close()

        logger.info("Pipeline finished successfully.")

    except Exception as e:
        logger.exception("Pipeline failed due to an unexpected error.")
        raise

if __name__ == "__main__":
    main()
