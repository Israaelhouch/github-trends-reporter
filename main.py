# main.py

from src.fetcher import github_api
from src.processor import analyze_trends
from src.notifier import email_notifier
from utils.logger import setup_logger

logger = setup_logger()

def main():
    logger.info("Starting GitHub Trends Reporter pipeline...")

    # Fetch trending repos
    try:
        trends = github_api.fetch_trending_repos()
        logger.info(f"Fetched {len(trends)} trending repositories.")
    except Exception as e:
        logger.exception("Error fetching trending repositories")
        return

    # Analyze trends
    try:
        analysis = analyze_trends.process_trends(trends)
        logger.info("Trend analysis completed.")
    except Exception as e:
        logger.exception("Error processing trends")
        return

    # Send email report
    try:
        email_notifier.send_report(analysis)
        logger.info("Email report sent successfully.")
    except Exception as e:
        logger.exception("Error sending email report")
        return

    logger.info("Pipeline finished successfully.")

if __name__ == "__main__":
    main()
