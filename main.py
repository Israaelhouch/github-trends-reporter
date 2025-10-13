from src.fetcher.fetching_pipline import run_fetch
from src.processor.processing_pipline import run_preprocess
from src.utils.logger import setup_logger

logger = setup_logger()

def main():
    logger.info("Starting GitHub Trends Reporter pipeline...")

    trends = run_fetch("machine learning", 200)
    run_preprocess(topic="machine learning")

    logger.info("Pipeline finished successfully.")

if __name__ == "__main__":
    main()
