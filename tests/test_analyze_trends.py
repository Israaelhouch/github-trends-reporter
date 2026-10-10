import json

import pandas as pd

from src.processor.analyze_trends import analyze_trends, extract_keywords
from tests.conftest import make_repo


def test_baseline_without_previous(current_df):
    results = analyze_trends(current_df, None, topic="ml")
    assert results["has_comparison"] is False
    assert "fastest_growing_repos" not in results
    json.dumps(results)  # must be serialisable (no numpy types)


def test_fork_count_is_counted_before_filtering(current_df):
    results = analyze_trends(current_df, None, topic="ml")
    assert results["forked_repos"] == 1  # used to always be 0
    assert results["total_repos"] == 3
    assert all(r["full_name"] != "someone/fork" for r in results["top_repos"])


def test_comparison_outputs_dicts_with_urls(current_df, previous_df):
    results = analyze_trends(current_df, previous_df, topic="ml")
    assert results["has_comparison"] is True

    new = results["new_trending_repos"]
    assert [r["full_name"] for r in new] == ["new/<script>"]
    assert new[0]["html_url"].startswith("https://github.com/")  # used to be bare strings

    growing = results["fastest_growing_repos"]
    assert growing[0]["full_name"] == "org/beta"
    assert growing[0]["stars_gained"] == 600
    assert growing[0]["html_url"] == "https://github.com/org/beta"  # used to be missing
    assert results["stars_gained_total"] == 900
    assert results["dropped_out_count"] == 1
    json.dumps(results)


def test_growth_pct_ignores_tiny_repos():
    prev = pd.DataFrame([make_repo("a/tiny", 10), make_repo("a/big", 1_000)])
    curr = pd.DataFrame([make_repo("a/tiny", 100), make_repo("a/big", 1_100)])
    results = analyze_trends(curr, prev, topic="ml")
    assert [r["full_name"] for r in results["fastest_growth_pct"]] == ["a/big"]


def test_rising_repos_included(current_df):
    rising = pd.DataFrame([make_repo("fresh/agent", 3_000)])
    results = analyze_trends(current_df, None, topic="ml", rising=rising)
    assert results["rising_repos"][0]["full_name"] == "fresh/agent"


def test_keywords_prefer_topics():
    df = pd.DataFrame([make_repo(f"o/r{i}", 1, topics="llm,agents") for i in range(15)])
    assert list(extract_keywords(df))[:2] == ["llm", "agents"]


def test_keywords_fall_back_to_descriptions():
    df = pd.DataFrame([make_repo("o/r", 1, topics="", description="Fast transformer inference engine")])
    kw = extract_keywords(df)
    assert "transformer" in kw and "the" not in kw
