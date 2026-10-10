"""Render a trend report (the dict from `analyze_trends`, plus optional `ai_insights`) as
an email subject, an HTML email, plain text, or Markdown."""

from html import escape


def _stars(n) -> str:
    return f"{int(n or 0):,}"


def _sections(results: dict) -> list[tuple[str, list[dict], str]]:
    """(title, repos, metric) for each repo list in the report, in display order."""
    sections = []
    if results.get("fastest_growing_repos"):
        sections.append(("🚀 Fastest growing this week", results["fastest_growing_repos"][:8], "gained"))
    if results.get("rising_repos"):
        sections.append(("🌱 Rising newcomers (recently created)", results["rising_repos"][:8], "stars"))
    if results.get("new_trending_repos"):
        sections.append(("🆕 New in the top list", results["new_trending_repos"][:8], "stars"))
    if results.get("top_repos"):
        sections.append(("⭐ All-time top repositories", results["top_repos"][:10], "stars"))
    return sections


def _metric(repo: dict, metric: str) -> str:
    if metric == "gained":
        pct = repo.get("stars_growth_pct")
        suffix = f" ({pct:+.1f}%)" if pct is not None else ""
        return f"+{_stars(repo.get('stars_gained'))} ★{suffix}"
    return f"{_stars(repo.get('stargazers_count'))} ★"


def generate_email_subject(results: dict) -> str:
    ai = results.get("ai_insights") or {}
    base = f"GitHub Trends: {results.get('topic', '').title()} ({results.get('date')})"
    return f"{base} — {ai['headline']}" if ai.get("headline") else base


def generate_markdown(results: dict) -> str:
    topic, date = results.get("topic", ""), results.get("date", "")
    lines = [f"# GitHub Trends — {topic.title()} ({date})", ""]

    stats = [f"**{results.get('total_repos', 0)}** repos tracked", f"**{_stars(results.get('total_stars'))}** total ★"]
    if results.get("has_comparison"):
        stats.append(f"**+{_stars(results.get('stars_gained_total'))}** ★ since {results.get('previous_date')}")
    else:
        stats.append("_baseline run — growth appears from the next run_")
    lines += [" · ".join(stats), ""]

    ai = results.get("ai_insights")
    if ai:
        lines += [f"## 🤖 AI summary: {ai['headline']}", "", ai["executive_summary"], ""]
        if ai.get("key_themes"):
            lines += ["**Key themes:** " + " · ".join(ai["key_themes"]), ""]
        if ai.get("notable_repos"):
            lines += ["| Repository | Category | Why it matters |", "|---|---|---|"]
            for r in ai["notable_repos"]:
                lines.append(
                    f"| [{r['full_name']}](https://github.com/{r['full_name']}) | {r['category']} "
                    f"| {r['why_it_matters'].replace('|', '/')} |"
                )
            lines.append("")
        if ai.get("model"):
            lines += [f"<sub>Summary written by the open model `{ai['model']}` via Ollama.</sub>", ""]

    for title, repos, metric in _sections(results):
        lines += [f"## {title}", ""]
        for r in repos:
            desc = (r.get("description") or "").replace("\n", " ").strip()
            desc = f" — {desc[:140]}" if desc else ""
            lines.append(f"- [{r['full_name']}]({r['html_url']}) · {_metric(r, metric)}{desc}")
        lines.append("")

    if results.get("top_languages"):
        lines += ["## 🏷️ Languages", "", "| Language | Repos | Share |", "|---|---:|---:|"]
        share = results.get("language_share", {})
        lines += [f"| {k} | {v} | {share.get(k, 0)}% |" for k, v in results["top_languages"].items()]
        lines.append("")
    if results.get("keywords"):
        lines += ["## 💡 Top topics", "", ", ".join(f"`{k}`" for k in results["keywords"]), ""]

    lines.append("<sub>Generated automatically by github-trends-reporter.</sub>")
    return "\n".join(lines) + "\n"


def generate_text(results: dict) -> str:
    lines = [generate_email_subject(results), "=" * 60]
    ai = results.get("ai_insights")
    if ai:
        lines += ["", ai["executive_summary"]]
    for title, repos, metric in _sections(results):
        lines += ["", title]
        lines += [f"  • {r['full_name']} ({_metric(r, metric)})  {r['html_url']}" for r in repos]
    return "\n".join(lines) + "\n"


_LI = "background:#f6f8fa;margin:2px 0;padding:4px 8px;border-radius:4px;font-size:13px;"
_A = "text-decoration:none;color:#0366d6;font-weight:600;"
_H3 = "margin:14px 0 4px;font-size:15px;"


def generate_html(results: dict) -> str:
    e = escape
    topic, date = e(str(results.get("topic", "")).title()), e(str(results.get("date", "")))
    out = [
        "<html><body style='font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#24292f;"
        "background:#fafafa;margin:0;padding:0;'>",
        "<div style='max-width:700px;margin:12px auto;padding:18px;background:#fff;border-radius:8px;"
        "box-shadow:0 1px 4px rgba(0,0,0,.1);line-height:1.4;'>",
        f"<h2 style='color:#1a73e8;margin:0 0 6px;font-size:19px;'>GitHub Trends — {topic}</h2>",
        f"<p style='margin:0 0 8px;font-size:13px;color:#57606a;'>{date} · {results.get('total_repos', 0)} repos"
        f" · {_stars(results.get('total_stars'))} ★"
        + (
            f" · <b>+{_stars(results.get('stars_gained_total'))} ★</b> since {e(str(results.get('previous_date')))}"
            if results.get("has_comparison")
            else " · baseline run"
        )
        + "</p>",
    ]

    ai = results.get("ai_insights")
    if ai:
        out.append(
            "<div style='background:#eef6ff;border-left:4px solid #1a73e8;padding:10px 12px;"
            "border-radius:4px;margin:10px 0;'>"
        )
        out.append(f"<div style='font-weight:600;margin-bottom:4px;'>🤖 {e(ai['headline'])}</div>")
        out.append(f"<div style='font-size:13px;'>{e(ai['executive_summary'])}</div>")
        if ai.get("key_themes"):
            out.append(
                "<div style='font-size:12px;margin-top:6px;color:#57606a;'>"
                + " · ".join(e(t) for t in ai["key_themes"])
                + "</div>"
            )
        if ai.get("model"):
            out.append(f"<div style='font-size:11px;margin-top:6px;color:#8c959f;'>AI summary · {e(ai['model'])}</div>")
        out.append("</div>")

    for title, repos, metric in _sections(results):
        out.append(f"<h3 style='{_H3}'>{e(title)}</h3><ul style='list-style:none;padding:0;margin:0;'>")
        for r in repos:
            desc = e((r.get("description") or "")[:120])
            out.append(
                f"<li style='{_LI}'><a href='{e(r['html_url'], quote=True)}' style='{_A}'>{e(r['full_name'])}</a>"
                f" — {e(_metric(r, metric))}"
                + (f"<br><span style='color:#57606a;'>{desc}</span>" if desc else "")
                + "</li>"
            )
        out.append("</ul>")

    if results.get("keywords"):
        out.append(
            f"<h3 style='{_H3}'>💡 Top topics</h3><p style='font-size:13px;margin:0;'>"
            + ", ".join(e(k) for k in results["keywords"])
            + "</p>"
        )

    out.append(
        "<hr style='margin:14px 0 6px;border:none;border-top:1px solid #eee;'>"
        "<p style='text-align:center;font-size:11px;color:#8c959f;margin:0;'>"
        "Generated automatically by github-trends-reporter</p></div></body></html>"
    )
    return "\n".join(out)
