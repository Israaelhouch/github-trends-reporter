"""LLM-generated narrative insights on top of the numeric trend report.

Runs a small open-source model through Ollama (free, local or inside GitHub Actions). The model's
output is constrained to a JSON schema derived from Pydantic models, validated, and then checked
against the input so it can't introduce repositories that aren't in the data. Entirely optional:
if Ollama isn't reachable or anything fails, the pipeline continues without the AI section.
"""

import json
import logging
import re
from collections import Counter
from typing import Literal

import requests
from pydantic import BaseModel, Field, ValidationError

from src import config

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 2
# Week-over-week language. ("gained 500 stars" alone is fine: for a new repo that's simply its total.)
_GROWTH_WORDS = re.compile(
    r"\b(?:this|last|past|previous) week\b|\bsince last\b|\bweek-over-week\b|\bgrowth\b|\bgrew\b"
    r"|\bmomentum\b|\bincreas\w*",
    re.I,
)

Category = Literal[
    "LLMs & Agents",
    "Generative Media",
    "Computer Vision",
    "NLP & Speech",
    "MLOps & Infrastructure",
    "Frameworks & Libraries",
    "Classical ML & Data Science",
    "Learning Resources",
    "Other",
]


class RepoInsight(BaseModel):
    full_name: str = Field(description="Exactly as written in the input, e.g. 'owner/repo'")
    category: Category
    why_it_matters: str = Field(description="One short sentence for a busy ML engineer")


class TrendInsights(BaseModel):
    headline: str = Field(description="One-sentence headline for this week's report")
    executive_summary: str = Field(description="2-4 sentences, using only facts from the input")
    key_themes: list[str] = Field(description="3-5 short themes visible in the data")
    notable_repos: list[RepoInsight] = Field(description="Up to 6 repositories from the input worth a closer look")


SYSTEM_PROMPT = """You write a short weekly briefing about GitHub repositories for AI/ML engineers.
You receive data computed from the GitHub API about one topic.

Rules:
- Use only facts present in the data. Never invent repositories, numbers, events, or trends.
- Prefer what is new: star growth and recently created "rising" repositories, not the all-time leaderboard.
- Copy repository names exactly as written in the data.

Output fields:
- headline: one specific sentence naming at least one repository or concrete trend. Not generic.
- executive_summary: 2-3 complete sentences with concrete names and numbers from the data.
- key_themes: 3-5 short labels of 2-4 words each, e.g. "AI engineering courses".
- notable_repos: 3-6 repositories from the data. For each, pick the closest category and write one
  short sentence (max 20 words) on why it matters.

Categories:
- LLMs & Agents: language models, chatbots, RAG, agent frameworks
- Generative Media: image, video, audio or 3D generation
- Computer Vision: detection, segmentation, OCR, image analysis
- NLP & Speech: text processing, translation, speech recognition
- MLOps & Infrastructure: training/serving infrastructure, hardware, compilers, deployment
- Frameworks & Libraries: general-purpose ML libraries and toolkits
- Classical ML & Data Science: tabular ML, statistics, notebooks, small applied projects
- Learning Resources: courses, tutorials, books, roadmaps, curated "awesome" lists
- Other: anything else"""


def _context_note(analysis: dict) -> str:
    if analysis.get("has_comparison"):
        return (
            f"Star growth is measured against the snapshot from {analysis.get('previous_date')}; "
            "'stars_gained' is the growth since then."
        )
    return (
        "This is the first run, so there is NO previous week to compare against. Do not use words like "
        "growth, gaining, momentum, or 'this week'. Describe the recently created repositories and the "
        "overall landscape. 'stargazers_count' is a total, not a change."
    )


def _compact_payload(analysis: dict, max_items: int = 8) -> dict:
    """Keep the prompt small enough for a 3B model on a CPU: few fields, short descriptions."""

    def slim(repos: list[dict]) -> list[dict]:
        keep = ("full_name", "stargazers_count", "stars_gained", "language")
        return [
            {k: r[k] for k in keep if r.get(k) is not None} | {"description": (r.get("description") or "")[:120]}
            for r in repos[:max_items]
        ]

    payload = {k: analysis.get(k) for k in ("topic", "date", "has_comparison", "stars_gained_total")}
    payload["top_languages"] = dict(list(analysis.get("top_languages", {}).items())[:5])
    # Neutral names so a small model doesn't read "rising" or "trending" as measured growth.
    sections = {
        "fastest_growing_repos": "repos_with_most_stars_gained",
        "rising_repos": "recently_created_repos",
        "new_trending_repos": "new_in_top_list",
        "top_repos": "all_time_top_repos",
    }
    for key, name in sections.items():
        if analysis.get(key):
            payload[name] = slim(analysis[key])
    return payload


def _known_repos(analysis: dict) -> set[str]:
    keys = ("top_repos", "rising_repos", "new_trending_repos", "fastest_growing_repos", "fastest_growth_pct")
    return {r["full_name"] for k in keys for r in analysis.get(k) or []}


def _growth_claim(insights: TrendInsights) -> str | None:
    """The first phrase that talks about change over time - only valid when there is a previous snapshot."""
    text = " ".join([insights.headline, insights.executive_summary, *insights.key_themes])
    match = _GROWTH_WORDS.search(text)
    return match.group(0) if match else None


def generate_insights(analysis: dict, session: requests.Session | None = None) -> dict | None:
    """Return the insights as a dict, or None when the model is unavailable or the output is unusable."""
    session = session or requests.Session()
    url = f"{config.OLLAMA_HOST.rstrip('/')}/api/chat"
    body = {
        "model": config.AI_MODEL,
        "stream": False,
        "format": TrendInsights.model_json_schema(),  # constrained decoding to this schema
        "options": {"temperature": 0.2, "num_ctx": 8192},
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"{_context_note(analysis)}\n\nData:\n"
                + json.dumps(_compact_payload(analysis), ensure_ascii=False, default=str),
            },
        ],
    }

    insights, data = None, {}
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = session.post(url, json=body, timeout=config.AI_TIMEOUT)
        except requests.ConnectionError:
            logger.info("Ollama not reachable at %s - skipping AI insights.", config.OLLAMA_HOST)
            return None
        except requests.RequestException as exc:
            logger.warning("Ollama request failed: %s", exc)
            return None
        if not response.ok:
            logger.warning("Ollama returned HTTP %s: %s", response.status_code, response.text[:200])
            return None

        data = response.json()
        try:
            candidate = TrendInsights.model_validate_json(data["message"]["content"])
        except (KeyError, ValidationError) as exc:
            logger.warning("Attempt %d: output did not match the schema: %s", attempt, str(exc)[:200])
            continue
        claim = None if analysis.get("has_comparison") else _growth_claim(candidate)
        if claim:
            logger.warning("Attempt %d: summary claims growth (%r) but there is no previous week", attempt, claim)
            # Self-correction: show the model its answer and the specific problem, then ask again.
            body["messages"] = body["messages"][:2] + [
                {"role": "assistant", "content": data["message"]["content"]},
                {
                    "role": "user",
                    "content": f"Your answer says {claim!r}, but there is no previous week in the data, so "
                    "nothing about growth or change is known. Rewrite the whole answer without any claim "
                    "about growth, gains, momentum, or this/last week.",
                },
            ]
            continue
        insights = candidate
        break

    if insights is None:
        logger.warning("No usable AI output after %d attempts - skipping the AI section.", MAX_ATTEMPTS)
        return None

    # Grounding check: drop any repository the model made up, and de-duplicate.
    known, seen, notable = _known_repos(analysis), set(), []
    for repo in insights.notable_repos:
        if repo.full_name in known and repo.full_name not in seen:
            seen.add(repo.full_name)
            notable.append(repo)
    dropped = len(insights.notable_repos) - len(notable)
    if dropped:
        logger.warning("Dropped %d AI-suggested repos that are not in the data", dropped)
    insights.notable_repos = notable

    logger.info(
        "AI insights from %s in %.1fs (%s prompt / %s output tokens)",
        config.AI_MODEL,
        data.get("total_duration", 0) / 1e9,
        data.get("prompt_eval_count"),
        data.get("eval_count"),
    )
    result = insights.model_dump()
    result["model"] = config.AI_MODEL
    result["category_breakdown"] = dict(Counter(r.category for r in notable).most_common())
    return result
