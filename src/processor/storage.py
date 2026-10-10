import json
import logging
import os

logger = logging.getLogger(__name__)


def slugify(topic: str) -> str:
    return "_".join(topic.lower().split())


def save_analysis(data: dict, topic: str, output_dir: str) -> str:
    """Write the analysis as `analysis_<topic>_<date>.json` and return the path."""
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"analysis_{slugify(topic)}_{data['date']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)
    logger.info("Analysis saved to %s", path)
    return path


def save_report(markdown: str, topic: str, date: str, reports_dir: str) -> str:
    """Write a dated Markdown report plus `LATEST.md`, which the README links to."""
    os.makedirs(reports_dir, exist_ok=True)
    path = os.path.join(reports_dir, f"{date}_{slugify(topic)}.md")
    for target in (path, os.path.join(reports_dir, "LATEST.md")):
        with open(target, "w", encoding="utf-8") as f:
            f.write(markdown)
    logger.info("Markdown report saved to %s", path)
    return path
