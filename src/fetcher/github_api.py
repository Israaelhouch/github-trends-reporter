"""Thin client for the GitHub Search API with auth, pagination, retries and rate-limit handling."""

import logging
import time
from datetime import date, timedelta

import pandas as pd
import requests

from src import config

logger = logging.getLogger(__name__)

REPO_COLUMNS = [
    "full_name",
    "html_url",
    "description",
    "stargazers_count",
    "forks_count",
    "open_issues_count",
    "language",
    "topics",
    "owner",
    "fork",
    "created_at",
    "updated_at",
    "pushed_at",
]


class GitHubAPIError(RuntimeError):
    pass


def build_session(token: str | None = config.GITHUB_TOKEN) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "github-trends-reporter",
        }
    )
    if token:
        session.headers["Authorization"] = f"Bearer {token}"
    else:
        logger.warning("GITHUB_TOKEN not set: using the unauthenticated search limit (10 req/min).")
    return session


def _rate_limit_wait(response: requests.Response, attempt: int) -> float:
    """Seconds to wait before retrying a rate-limited request."""
    retry_after = response.headers.get("Retry-After")
    if retry_after:
        return float(retry_after)
    reset = response.headers.get("X-RateLimit-Reset")
    if reset and response.headers.get("X-RateLimit-Remaining") == "0":
        return max(float(reset) - time.time(), 0) + 1
    return 2**attempt * 5


def _get_page(session: requests.Session, params: dict, sleep=time.sleep) -> list[dict]:
    for attempt in range(config.MAX_RETRIES + 1):
        try:
            response = session.get(config.GITHUB_API_URL, params=params, timeout=config.REQUEST_TIMEOUT)
        except requests.RequestException as exc:
            if attempt == config.MAX_RETRIES:
                raise GitHubAPIError(f"Network error calling GitHub: {exc}") from exc
            wait = 2**attempt
            logger.warning("Request error (%s), retrying in %ss", exc, wait)
            sleep(wait)
            continue

        if response.status_code in (403, 429) and attempt < config.MAX_RETRIES:
            wait = min(_rate_limit_wait(response, attempt), 120)
            logger.warning("Rate limited (HTTP %s), retrying in %.0fs", response.status_code, wait)
            sleep(wait)
            continue
        if response.status_code >= 500 and attempt < config.MAX_RETRIES:
            wait = 5 * 2**attempt
            logger.warning("GitHub server error (HTTP %s), retrying in %ss", response.status_code, wait)
            sleep(wait)
            continue
        if not response.ok:
            raise GitHubAPIError(f"GitHub API returned {response.status_code}: {response.text[:300]}")
        return response.json().get("items", [])
    raise GitHubAPIError("Exhausted retries calling GitHub")


def search_repos(
    query: str, limit: int, session: requests.Session | None = None, delay: float = 1.0, sleep=time.sleep
) -> pd.DataFrame:
    """Return up to `limit` repositories matching `query`, sorted by stars (desc)."""
    session = session or build_session()
    repos: list[dict] = []
    page = 1
    while len(repos) < limit:
        params = {"q": query, "sort": "stars", "order": "desc", "per_page": config.PER_PAGE, "page": page}
        logger.info("GitHub search page %s: %s", page, query)
        items = _get_page(session, params, sleep=sleep)
        repos.extend(items)
        if len(items) < config.PER_PAGE:
            break  # last page
        page += 1
        sleep(delay)

    df = pd.DataFrame([_flatten(r) for r in repos[:limit]], columns=REPO_COLUMNS)
    logger.info("Fetched %d repositories for query %r", len(df), query)
    return df


def _flatten(repo: dict) -> dict:
    return {
        "full_name": repo["full_name"],
        "html_url": repo["html_url"],
        "description": repo.get("description") or "",
        "stargazers_count": repo.get("stargazers_count", 0),
        "forks_count": repo.get("forks_count", 0),
        "open_issues_count": repo.get("open_issues_count", 0),
        "language": repo.get("language"),
        "topics": ",".join(repo.get("topics") or []),
        "owner": (repo.get("owner") or {}).get("login"),
        "fork": bool(repo.get("fork")),
        "created_at": repo.get("created_at"),
        "updated_at": repo.get("updated_at"),
        "pushed_at": repo.get("pushed_at"),
    }


def fetch_top_repos(topic: str, top_n: int, **kwargs) -> pd.DataFrame:
    """All-time most-starred repositories for a topic (used for week-over-week growth)."""
    return search_repos(f"{topic} in:name,description,topics", top_n, **kwargs)


def fetch_rising_repos(topic: str, days: int, limit: int, today: date | None = None, **kwargs) -> pd.DataFrame:
    """Most-starred repositories *created* in the last `days` days - the actually new stuff."""
    since = (today or date.today()) - timedelta(days=days)
    return search_repos(f"{topic} in:name,description,topics created:>={since.isoformat()}", limit, **kwargs)
