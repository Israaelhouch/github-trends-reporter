# 📈 GitHub Trends Reporter

[![CI](https://github.com/Israaelhouch/github-trends-reporter/actions/workflows/ci.yml/badge.svg)](https://github.com/Israaelhouch/github-trends-reporter/actions/workflows/ci.yml)
[![Weekly report](https://github.com/Israaelhouch/github-trends-reporter/actions/workflows/weekly-report.yml/badge.svg)](https://github.com/Israaelhouch/github-trends-reporter/actions/workflows/weekly-report.yml)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![LLM](https://img.shields.io/badge/LLM-Ollama%20·%20open%20models-black)

**Every week, find out what's growing in the ML ecosystem on GitHub, with a summary written by a free open-source LLM.**

The pipeline tracks the top 200 repositories for a topic, measures their week-over-week star growth, spots newly
created repos that are taking off, and sends the results as an email and a Markdown report.
It runs on GitHub Actions with **no paid APIs and no API keys**.

👉 **[Latest report](reports/LATEST.md)**

<p align="center">
  <img src="assets/email.png" alt="Weekly email with AI summary and rising repositories" width="720">
</p>

<details>
<summary>📄 The same report as Markdown in the repo (click to expand)</summary>
<p align="center"><img src="assets/report.png" alt="Markdown report" width="720"></p>
</details>

## How it works

```mermaid
flowchart LR
    A[GitHub API] --> B[Fetch top + rising repos]
    B --> C[(Weekly snapshots)]
    C --> D[Compare with last week]
    D --> E[Open LLM summary<br/>Ollama]
    E --> F[Email + Markdown report]
```

1. **Fetch** the all-time top repos and the most-starred repos created in the last 30 days.
2. **Snapshot** each repo's star count. A run adds an ~8 KB CSV, committed to the repo.
3. **Compare** with last week's snapshot: fastest growing repos, new entries, languages, topics.
4. **Summarize** with `qwen2.5:3b` running in Ollama, which writes a headline, summary, themes and per-repo categories.
5. **Deliver** the report to `reports/` (committed automatically) and by email.

## The AI part

The summary is written by a small, free model (`qwen2.5:3b`). Small models sometimes make mistakes, so the code
checks every answer before it is published:

| What can go wrong | How it's handled |
|---|---|
| Malformed output | Output is constrained to a JSON schema (Pydantic) and validated |
| Made-up repositories | Any repo that isn't in the input data is removed |
| False claims, e.g. "grew this week" on a first run | Detected in code. The model gets its own answer back with the problem and retries. |
| Ollama down, or output still bad | The AI section is skipped and the rest of the report is still sent |

Each summary takes about 5–9 s on a laptop CPU. See [`src/ai/insights.py`](src/ai/insights.py).

## Quick start

```bash
git clone https://github.com/Israaelhouch/github-trends-reporter.git
cd github-trends-reporter
make install

# Optional AI summary (free): install Ollama from https://ollama.com, then
ollama serve &
make ai-setup        # downloads qwen2.5:3b (~2 GB)

make run             # report → reports/LATEST.md
```

Other topics: `python main.py --topic "large language models" --no-email`.
Skip the AI step with `--no-ai`.

## Running it on GitHub Actions

It works out of the box. The weekly workflow (Mondays, 08:00 UTC) starts Ollama as a service container,
runs the pipeline, and commits the report. Run it manually from **Actions → Weekly GitHub Trends Report → Run workflow**.

Optional settings, under **Settings → Secrets and variables → Actions**:

| Name | Type | Purpose |
|---|---|---|
| `EMAIL_USER`, `EMAIL_PASS`, `EMAIL_TO` | Secrets | Send the report by email (Gmail needs an [App Password](https://support.google.com/accounts/answer/185833)) |
| `TOPIC` | Variable | Topic to track (default: `machine learning`) |
| `AI_MODEL` | Variable | Any Ollama model, e.g. `qwen2.5:7b` for better writing |
| `DATABASE_URL` | Secret | Store history in PostgreSQL instead of CSV files |

For local runs, the same settings go in `.env` (see [`.env.example`](.env.example)).

## Project layout

```
main.py              pipeline entry point
src/fetcher/         GitHub API client: pagination, retries, rate limits
src/db/history.py    weekly snapshots (CSV or SQL)
src/processor/       growth analysis
src/ai/insights.py   Ollama summary + guardrails
src/notifier/        email / Markdown templates
tests/               36 tests, no network needed
```

**Stack:** Python · pandas · SQLAlchemy · Pydantic · Ollama · GitHub Actions · Docker · pytest · ruff

```bash
make test   # run tests
make lint   # lint + format check
```

---

**Israa Elhouch** · [GitHub](https://github.com/Israaelhouch) · israa.elhouch.dev@gmail.com
