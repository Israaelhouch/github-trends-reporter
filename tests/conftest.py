import pandas as pd
import pytest


def make_repo(
    name: str,
    stars: int,
    *,
    fork: bool = False,
    language: str = "Python",
    topics: str = "machine-learning,deep-learning",
    description: str = "A repo",
) -> dict:
    owner = name.split("/")[0]
    return {
        "full_name": name,
        "html_url": f"https://github.com/{name}",
        "description": description,
        "stargazers_count": stars,
        "forks_count": 1,
        "open_issues_count": 0,
        "language": language,
        "topics": topics,
        "owner": owner,
        "fork": fork,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2025-01-01T00:00:00Z",
        "pushed_at": "2025-01-01T00:00:00Z",
    }


@pytest.fixture
def previous_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            make_repo("org/alpha", 10_000),
            make_repo("org/beta", 5_000, language="C++"),
            make_repo("solo/gone", 900),
        ]
    )


@pytest.fixture
def current_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            make_repo("org/alpha", 10_300),
            make_repo("org/beta", 5_600, language="C++"),
            make_repo("new/<script>", 2_000, description="<b>xss</b> attempt"),
            make_repo("someone/fork", 50_000, fork=True),
        ]
    )
