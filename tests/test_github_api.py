from datetime import date

import pytest

from src.fetcher import github_api


class FakeResponse:
    def __init__(self, status=200, items=None, headers=None):
        self.status_code = status
        self._items = items or []
        self.headers = headers or {}
        self.text = "error"

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        return {"items": self._items}


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.headers = {}

    def get(self, url, params=None, timeout=None):
        self.calls.append(params)
        return self.responses.pop(0)


def api_item(i: int) -> dict:
    return {
        "full_name": f"o/r{i}",
        "html_url": f"https://github.com/o/r{i}",
        "stargazers_count": 1000 - i,
        "owner": {"login": "o"},
        "fork": False,
        "topics": ["ml", "ai"],
        "language": "Python",
        "description": None,
        "created_at": "2025-01-01T00:00:00Z",
    }


def test_token_is_sent_as_bearer():
    session = github_api.build_session(token="abc")
    assert session.headers["Authorization"] == "Bearer abc"


def test_paginates_and_truncates():
    pages = [
        FakeResponse(items=[api_item(i) for i in range(100)]),
        FakeResponse(items=[api_item(i) for i in range(100, 200)]),
    ]
    session = FakeSession(pages)
    df = github_api.search_repos("ml", 150, session=session, sleep=lambda s: None)
    assert len(df) == 150
    assert [c["page"] for c in session.calls] == [1, 2]
    assert df.loc[0, "topics"] == "ml,ai"
    assert df.loc[0, "description"] == ""


def test_stops_on_short_page():
    session = FakeSession([FakeResponse(items=[api_item(1), api_item(2)])])
    df = github_api.search_repos("ml", 200, session=session, sleep=lambda s: None)
    assert len(df) == 2 and len(session.calls) == 1


def test_rate_limit_is_retried_not_skipped():
    # Regression: a 403 used to skip the page entirely.
    waits = []
    session = FakeSession(
        [
            FakeResponse(403, headers={"Retry-After": "7"}),
            FakeResponse(items=[api_item(1)]),
        ]
    )
    df = github_api.search_repos("ml", 10, session=session, sleep=waits.append)
    assert len(df) == 1
    assert waits == [7.0]


def test_hard_errors_raise():
    session = FakeSession([FakeResponse(422)])
    with pytest.raises(github_api.GitHubAPIError):
        github_api.search_repos("ml", 10, session=session, sleep=lambda s: None)


def test_rising_query_has_created_filter():
    session = FakeSession([FakeResponse(items=[])])
    github_api.fetch_rising_repos("llm", 30, 10, today=date(2026, 10, 10), session=session, sleep=lambda s: None)
    assert "created:>=2026-09-10" in session.calls[0]["q"]


def test_server_errors_are_retried_with_backoff():
    waits = []
    session = FakeSession([FakeResponse(502), FakeResponse(500), FakeResponse(items=[api_item(1)])])
    df = github_api.search_repos("ml", 10, session=session, sleep=waits.append)
    assert len(df) == 1
    assert waits == [5, 10]
