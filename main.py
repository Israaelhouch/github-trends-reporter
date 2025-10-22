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
    parser.add_argument("--topic", type=str, default=None)
    parser.add_argument("--top_n", type=int, default=200)
    args = parser.parse_args()

    topic = args.topic or TOPIC
    top_n = args.top_n or TOP_N
    logger.info(f"Pipeline started for topic '{topic}'")

    db = GitHubDB()
    db.connect()

    try:
        run_fetch(topic=topic, top_n=top_n, db=db)
        run_preprocess(topic=topic, db=db)
        run_notifier(topic=topic)
        logger.info("Pipeline finished successfully.")
    except Exception:
        logger.exception("Pipeline failed due to an error.")
        raise
    finally:
        db.close() 

if __name__ == "__main__":
    main()