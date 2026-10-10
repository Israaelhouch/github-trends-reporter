import json

import requests

from src import config
from src.ai import insights

ANALYSIS = {
    "topic": "ml",
    "has_comparison": False,
    "top_repos": [{"full_name": "org/alpha", "stargazers_count": 10, "description": "x" * 500}],
    "rising_repos": [{"full_name": "new/agent", "stargazers_count": 5, "description": "agents"}],
    "irrelevant": "should not be sent",
}

GOOD = {
    "headline": "Agents rising",
    "executive_summary": "Short summary.",
    "key_themes": ["agents"],
    "notable_repos": [
        {"full_name": "new/agent", "category": "LLMs & Agents", "why_it_matters": "New agent framework."},
        {"full_name": "made/up", "category": "Other", "why_it_matters": "Hallucinated."},
        {"full_name": "new/agent", "category": "LLMs & Agents", "why_it_matters": "Duplicate."},
    ],
}


class FakeResponse:
    def __init__(self, status=200, content=None):
        self.status_code, self.text = status, "err"
        self._data = {"message": {"content": content}, "prompt_eval_count": 10, "eval_count": 5}

    @property
    def ok(self):
        return self.status_code < 400

    def json(self):
        return self._data


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response, self.error, self.body = response, error, None

    def post(self, url, json=None, timeout=None):
        self.url, self.body = url, json
        if self.error:
            raise self.error
        return self.response


def test_valid_output_is_grounded_and_deduplicated():
    session = FakeSession(FakeResponse(content=json.dumps(GOOD)))
    result = insights.generate_insights(ANALYSIS, session)
    assert [r["full_name"] for r in result["notable_repos"]] == ["new/agent"]  # made-up + duplicate dropped
    assert result["category_breakdown"] == {"LLMs & Agents": 1}
    assert result["model"] == config.AI_MODEL


def test_request_uses_schema_and_compact_prompt():
    session = FakeSession(FakeResponse(content=json.dumps(GOOD)))
    insights.generate_insights(ANALYSIS, session)
    assert session.url.endswith("/api/chat")
    assert session.body["format"]["properties"]["notable_repos"]
    prompt = session.body["messages"][1]["content"]
    assert "irrelevant" not in prompt
    assert "x" * 121 not in prompt  # descriptions are truncated


def test_ollama_not_running_is_skipped():
    session = FakeSession(error=requests.ConnectionError())
    assert insights.generate_insights(ANALYSIS, session) is None


def test_invalid_json_is_skipped():
    assert insights.generate_insights(ANALYSIS, FakeSession(FakeResponse(content="not json"))) is None


def test_schema_mismatch_is_skipped():
    bad = json.dumps({"headline": "x"})  # missing required fields
    assert insights.generate_insights(ANALYSIS, FakeSession(FakeResponse(content=bad))) is None


def test_http_error_is_skipped():
    assert insights.generate_insights(ANALYSIS, FakeSession(FakeResponse(status=404))) is None


class SequenceSession(FakeSession):
    def __init__(self, contents):
        super().__init__()
        self.contents, self.calls = list(contents), 0

    def post(self, url, json=None, timeout=None):
        self.calls += 1
        return FakeResponse(content=self.contents.pop(0))


def test_growth_claim_without_history_is_retried():
    lying = json.dumps(GOOD | {"executive_summary": "Repos saw strong growth this week."})
    session = SequenceSession([lying, json.dumps(GOOD)])
    result = insights.generate_insights(ANALYSIS, session)
    assert session.calls == 2
    assert result["executive_summary"] == "Short summary."


def test_gives_up_after_max_attempts():
    lying = json.dumps(GOOD | {"headline": "Strong growth everywhere"})
    session = SequenceSession([lying] * insights.MAX_ATTEMPTS)
    assert insights.generate_insights(ANALYSIS, session) is None


def test_growth_words_allowed_when_history_exists():
    text = json.dumps(GOOD | {"executive_summary": "new/agent gained 300 stars this week."})
    result = insights.generate_insights(ANALYSIS | {"has_comparison": True}, SequenceSession([text]))
    assert "gained" in result["executive_summary"]


def test_star_totals_are_not_growth_claims():
    text = json.dumps(GOOD | {"executive_summary": "new/agent has gained 5 stars since it was created."})
    session = SequenceSession([text])
    assert insights.generate_insights(ANALYSIS, session) is not None
    assert session.calls == 1


def test_this_week_alone_is_not_a_growth_claim():
    text = json.dumps(GOOD | {"headline": "This week: agent frameworks lead the new repos"})
    session = SequenceSession([text])
    assert insights.generate_insights(ANALYSIS, session)["headline"].startswith("This week")
    assert session.calls == 1


def test_comparison_with_last_week_is_still_blocked():
    lying = json.dumps(GOOD | {"executive_summary": "More stars than last week."})
    assert insights.generate_insights(ANALYSIS, SequenceSession([lying] * insights.MAX_ATTEMPTS)) is None
