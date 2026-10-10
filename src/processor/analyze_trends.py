"""Turn repository snapshots into a JSON-serialisable trend report."""

import logging
import re
from collections import Counter
from datetime import UTC, datetime

import pandas as pd

logger = logging.getLogger(__name__)

REPO_FIELDS = ["full_name", "html_url", "description", "stargazers_count", "language"]
MIN_STARS_FOR_PCT = 500  # ignore % growth on tiny repos, where +10 stars looks like +100%

_STOPWORDS_TEXT = """
a an and are as at be by for from has have in into is it its of on or that the this to with your you our we
using use based via can will not all any more most new over than then these those what when which who how
also just like one two toolkit library
"""
_STOPWORDS = frozenset(_STOPWORDS_TEXT.split())


def _records(df: pd.DataFrame, cols: list[str]) -> list[dict]:
    cols = [c for c in cols if c in df.columns]
    out = df[cols].astype(object).where(df[cols].notna(), None).to_dict(orient="records")
    for rec in out:
        for k, v in rec.items():
            if hasattr(v, "item"):
                rec[k] = v.item()
    return out


def extract_keywords(df: pd.DataFrame, n: int = 15) -> dict[str, int]:
    """Most common GitHub topics, falling back to description words when topics are sparse."""
    counter: Counter[str] = Counter()
    for topics in df.get("topics", pd.Series(dtype=str)).fillna(""):
        counter.update(t for t in topics.split(",") if t)
    if sum(counter.values()) < 20:
        for desc in df.get("description", pd.Series(dtype=str)).fillna(""):
            words = re.findall(r"[a-z][a-z0-9+#-]{2,}", desc.lower())
            counter.update(w for w in words if w not in _STOPWORDS)
    return dict(counter.most_common(n))


def analyze_trends(
    current: pd.DataFrame, previous: pd.DataFrame | None, topic: str, rising: pd.DataFrame | None = None
) -> dict:
    logger.info("Analyzing %d repos for '%s'", len(current), topic)

    forked = int(current["fork"].astype(bool).sum())
    repos = current[~current["fork"].astype(bool)]
    total = len(repos)

    top_languages = repos["language"].value_counts().head(10)
    results: dict = {
        "date": datetime.now(UTC).strftime("%Y-%m-%d"),
        "topic": topic,
        "total_repos": total,
        "forked_repos": forked,
        "total_stars": int(repos["stargazers_count"].sum()),
        "top_languages": {k: int(v) for k, v in top_languages.items()},
        "language_share": {k: round(v / total * 100, 1) for k, v in top_languages.items()} if total else {},
        "top_organizations": {k: int(v) for k, v in repos["owner"].value_counts().head(10).items()},
        "top_repos": _records(repos.nlargest(10, "stargazers_count"), REPO_FIELDS),
        "keywords": extract_keywords(repos),
        "rising_repos": [],
        "has_comparison": False,
    }

    if rising is not None and not rising.empty:
        rising = rising[~rising["fork"].astype(bool)]
        results["rising_repos"] = _records(rising.nlargest(10, "stargazers_count"), REPO_FIELDS + ["created_at"])

    if previous is None or previous.empty:
        logger.info("No previous snapshot - skipping week-over-week comparison.")
        return results

    prev_names = set(previous["full_name"])
    curr_names = set(repos["full_name"])
    new_entries = repos[~repos["full_name"].isin(prev_names)]

    merged = repos.merge(previous[["full_name", "stargazers_count"]], on="full_name", suffixes=("", "_prev"))
    merged["stars_gained"] = merged["stargazers_count"] - merged["stargazers_count_prev"]
    merged["stars_growth_pct"] = (merged["stars_gained"] / merged["stargazers_count_prev"].clip(lower=1) * 100).round(2)
    gainers = merged[merged["stars_gained"] > 0]
    sized = gainers[gainers["stargazers_count_prev"] >= MIN_STARS_FOR_PCT]

    results.update(
        {
            "has_comparison": True,
            "previous_date": str(previous["snapshot_date"].iloc[0]) if "snapshot_date" in previous else None,
            "stars_gained_total": int(merged["stars_gained"].sum()),
            "new_trending_repos": _records(new_entries.nlargest(10, "stargazers_count"), REPO_FIELDS),
            "dropped_out_count": len(prev_names - curr_names),
            "fastest_growing_repos": _records(
                gainers.nlargest(10, "stars_gained"), REPO_FIELDS + ["stars_gained", "stars_growth_pct"]
            ),
            "fastest_growth_pct": _records(
                sized.nlargest(5, "stars_growth_pct"), REPO_FIELDS + ["stars_gained", "stars_growth_pct"]
            ),
        }
    )
    return results
