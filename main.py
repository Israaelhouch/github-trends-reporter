"""GitHub Trends Reporter - fetch -> snapshot -> analyze -> AI insights -> report -> email."""

import argparse
import logging
import time
from datetime import UTC, datetime

from src import config
from src.ai.insights import generate_insights
from src.db.history import open_history
from src.fetcher.pipeline import run_fetch
from src.notifier.mailer import EmailError
from src.notifier.pipeline import run_notifier
from src.notifier.templates import generate_markdown
from src.processor.analyze_trends import analyze_trends
from src.processor.storage import save_analysis, save_report
from src.utils.logger import setup_logging

logger = logging.getLogger("github_trends")


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GitHub Trends Reporter")
    parser.add_argument("--topic", default=config.TOPIC, help="Search topic (default: %(default)s)")
    parser.add_argument("--top-n", type=int, default=config.TOP_N, help="Top repos to track (default: %(default)s)")
    parser.add_argument(
        "--rising-days",
        type=int,
        default=config.RISING_DAYS,
        help="Window for 'rising' repos, in days (default: %(default)s)",
    )
    parser.add_argument("--rising-n", type=int, default=config.RISING_N)
    parser.add_argument("--no-ai", action="store_true", help="Skip the AI (Ollama) summary")
    parser.add_argument("--no-email", action="store_true", help="Skip sending the email")
    return parser.parse_args(argv)


def main(argv=None) -> int:
    """Run the pipeline. Returns the process exit code (1 if an optional step like email failed)."""
    args = parse_args(argv)
    setup_logging(config.LOG_DIR)
    start = time.time()
    logger.info("Pipeline started for topic '%s'", args.topic)

    top, rising = run_fetch(args.topic, args.top_n, args.rising_days, args.rising_n)

    today = datetime.now(UTC).date()
    history = open_history(config.DATABASE_URL, config.HISTORY_DIR)
    previous = history.load_previous(args.topic, before=today)
    history.save(top, args.topic, today)

    results = analyze_trends(top, previous, topic=args.topic, rising=rising)

    if not args.no_ai:
        insights = generate_insights(results)
        if insights:
            results["ai_insights"] = insights

    save_analysis(results, args.topic, config.DATA_OUTPUT_DIR)
    save_report(generate_markdown(results), args.topic, results["date"], config.REPORTS_DIR)

    exit_code = 0
    if not args.no_email:
        try:
            run_notifier(results)
        except EmailError as exc:
            logger.error("%s (The report and history were still saved.)", exc)
            exit_code = 1

    logger.info("Pipeline finished in %.1fs", time.time() - start)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
