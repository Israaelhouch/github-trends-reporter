import logging
import time

import pandas as pd

from .github_api import build_session, fetch_rising_repos, fetch_top_repos

logger = logging.getLogger(__name__)


def run_fetch(topic: str, top_n: int, rising_days: int, rising_n: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (all-time top repos, recently created rising repos) for a topic."""
    start = time.time()
    session = build_session()

    top = fetch_top_repos(topic, top_n, session=session)
    if top.empty:
        raise ValueError(f"No repositories fetched for topic '{topic}'")
    rising = fetch_rising_repos(topic, rising_days, rising_n, session=session)

    logger.info("Fetching finished in %.1fs", time.time() - start)
    return top, rising
