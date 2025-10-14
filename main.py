from src.fetcher.fetching_pipline import run_fetch
from src.processor.processing_pipline import run_preprocess
from src.notifier.notifying_pipline import run_notifier
from src.utils.logger import setup_logger

logger = setup_logger("auto_notifier")

def main():
    topic = "artificial intelligence"
    logger.info(f"Starting GitHub Trends Reporter pipeline for topic: '{topic}'")

    try:
        # Fetch stage
        trends = run_fetch(topic, 200)
        logger.info("Fetching completed successfully.")

        # Process stage
        run_preprocess(topic=topic)
        logger.info("Processing completed successfully.")

        # Notify stage
        run_notifier(topic=topic)
        logger.info("Notification sent successfully.")

        logger.info("Pipeline finished successfully.")

    except Exception as e:
        logger.exception("Pipeline failed due to an unexpected error.")
        raise

if __name__ == "__main__":
    main()
