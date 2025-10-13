from src.fetcher.fetching_pipline import run_fetch
from src.processor.processing_pipline import run_preprocess
from src.notifier.notifying_pipline import run_notifier
from src.utils.logger import setup_logger

logger = setup_logger()

def main():
    logger.info("Starting GitHub Trends Reporter pipeline...")
    topic="artificial intelligence"
    trends = run_fetch(topic, 200)
    run_preprocess(topic=topic)
    run_notifier(topic=topic)

    logger.info("Pipeline finished successfully.")

if __name__ == "__main__":
    main()
