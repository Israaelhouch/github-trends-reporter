from datetime import datetime

from datetime import datetime

def generate_email_subject(topic: str) -> str:
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    return f"📊 GitHub Trends Summary: {topic.title()} ({date_str})"

def generate_email_body(results: dict, html: bool = False) -> str:
    """
    Generate a professional GitHub Trend report email (plain text or HTML)
    from GitHub trend analysis results. Safe for all email clients.
    """
    topic = results.get("topic", "General")
    date = results.get("date", datetime.now().strftime("%Y-%m-%d"))
    total = results.get("total_repos", 0)
    forked = results.get("forked_repos", 0)

    # ---------- TEXT VERSION ----------
    if not html:
        lines = [
            f"📊 GitHub Trend Report — {topic}",
            f"📅 Date: {date}",
            f"📦 Total repositories: {total:,} | 🍴 Forked: {forked:,}",
            "─" * 60,
        ]

        # Top Languages
        top_langs = results.get("top_languages", {})
        if top_langs:
            lines.append("\n🏷️ Top Languages:")
            for lang, count in top_langs.items():
                lines.append(f"  • {lang}: {count}")

        # Top Organizations
        top_orgs = results.get("top_organizations", {})
        if top_orgs:
            lines.append("\n🏢 Top Organizations:")
            for org, count in top_orgs.items():
                lines.append(f"  • {org}: {count} repos")

        # Top Repositories
        top_repos = results.get("top_repos", [])
        if top_repos:
            lines.append("\n⭐ Top Repositories:")
            for r in top_repos[:10]:
                lines.append(f"  • {r['full_name']} ({r['stargazers_count']} ⭐)\n    🔗 {r['html_url']}")

        # Fastest Growing Repositories
        fastest_growing = results.get("fastest_growing_repos", [])
        if fastest_growing:
            lines.append("\n🚀 Fastest Growing Repositories:")
            for r in fastest_growing[:5]:
                lines.append(f"  • {r['full_name']} (+{r['stars_gained']} ⭐)\n    🔗 {r.get('html_url', '')}")

        # New Trending Repositories
        new_repos = results.get("new_trending_repos", [])
        if new_repos:
            lines.append("\n🆕 New Trending Repositories:")
            for r in new_repos[:5]:
                lines.append(f"  • {r['full_name']} ({r['stargazers_count']} ⭐)\n    🔗 {r.get('html_url', '')}")

        # Keywords
        keywords = results.get("keywords", {})
        if keywords:
            top_keywords = list(keywords.keys())[:10]
            lines.append("\n💡 Common Keywords:")
            lines.append(", ".join(top_keywords))

        lines.append("─" * 60)
        lines.append("📨 Report generated automatically by GitHub Trend Notifier 🚀")
        return "\n".join(lines)

    # ---------- HTML VERSION ----------
    else:
        html_lines = [
            "<html><body style='font-family:Segoe UI, Roboto, sans-serif; color:#333; background:#fafafa; margin:0; padding:0;'>",
            "<div style='max-width:700px; margin:10px auto; padding:15px; background:#fff; border-radius:8px; box-shadow:0 1px 4px rgba(0,0,0,0.1); line-height:1.25;'>",
            f"<h2 style='color:#1a73e8; border-bottom:1px solid #eaeaea; padding-bottom:4px; margin:0 0 6px 0; font-size:18px;'>📊 GitHub Trend Report — {topic}</h2>",
            f"<p style='margin:0 0 6px 0; font-size:14px;'><b>📅 Date:</b> {date}<br><b>📦 Total repositories:</b> {total:,} | 🍴 <b>Forked:</b> {forked:,}</p>",
            "<hr style='margin:6px 0;'>"
        ]

        def make_list(title, items):
            html_lines.append(f"<h3 style='margin:4px 0 2px 0; font-size:15px; font-weight:500;'>{title}</h3>")
            html_lines.append("<ul style='list-style:none; padding:0; margin:0;'>")
            html_lines.extend(items)
            html_lines.append("</ul>")

        # Top Languages
        top_langs = results.get("top_languages", {})
        if top_langs:
            make_list("🏷️ Top Languages", [
                f"<li style='background:#f6f8fa; margin:1px 0; padding:2px 6px; border-radius:4px; font-size:13px;'>{lang}: {count}</li>"
                for lang, count in top_langs.items()
            ])

        # Top Organizations
        top_orgs = results.get("top_organizations", {})
        if top_orgs:
            make_list("🏢 Top Organizations", [
                f"<li style='background:#f6f8fa; margin:1px 0; padding:2px 6px; border-radius:4px; font-size:13px;'>{org}: {count} repos</li>"
                for org, count in top_orgs.items()
            ])

        # Top Repositories
        top_repos = results.get("top_repos", [])
        if top_repos:
            make_list("⭐ Top Repositories", [
                f"<li style='background:#f6f8fa; margin:1px 0; padding:2px 6px; border-radius:4px; font-size:13px;'>"
                f"<a href='{r['html_url']}' target='_blank' style='text-decoration:none; color:#0366d6;'>{r['full_name']}</a> — {r['stargazers_count']} ⭐</li>"
                for r in top_repos[:10]
            ])

        # Fastest Growing Repos
        fastest_growing = results.get("fastest_growing_repos", [])
        if fastest_growing:
            make_list("🚀 Fastest Growing Repositories", [
                f"<li style='background:#e8f0fe; margin:1px 0; padding:2px 6px; border-radius:4px; font-size:13px;'>"
                f"<a href='{r.get('html_url','#')}' target='_blank' style='text-decoration:none; color:#0366d6;'>{r['full_name']}</a> — +{r['stars_gained']} ⭐</li>"
                for r in fastest_growing[:5]
            ])

        # New Trending Repos
        new_repos = results.get("new_trending_repos", [])
        if new_repos:
            make_list("🆕 New Trending Repositories", [
                f"<li style='background:#e8f0fe; margin:1px 0; padding:2px 6px; border-radius:4px; font-size:13px;'>"
                f"<a href='{r.get('html_url','#')}' target='_blank' style='text-decoration:none; color:#0366d6;'>{r['full_name']}</a> — {r['stargazers_count']} ⭐</li>"
                for r in new_repos[:5]
            ])

        # Keywords
        keywords = results.get("keywords", {})
        if keywords:
            top_keywords = list(keywords.keys())[:10]
            html_lines.append("<h3 style='margin:4px 0 2px 0; font-size:15px;'>💡 Common Keywords</h3>")
            html_lines.append(f"<p style='margin:0 0 6px 0; font-size:13px;'>{', '.join(top_keywords)}</p>")

        html_lines.append("<hr style='margin:6px 0;'><p style='text-align:center; font-size:11px; color:#777; margin:0;'><i>📨 Report generated automatically by <b>GitHub Trend Notifier</b> 🚀</i></p>")
        html_lines.append("</div></body></html>")

        return "\n".join(html_lines)
