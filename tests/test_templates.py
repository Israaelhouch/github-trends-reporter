from src.notifier.templates import generate_email_subject, generate_html, generate_markdown, generate_text
from src.processor.analyze_trends import analyze_trends

AI = {
    "headline": "Agents keep climbing",
    "executive_summary": "Summary <with> markup.",
    "key_themes": ["agents", "inference"],
    "notable_repos": [{"full_name": "org/beta", "category": "LLMs & Agents", "why_it_matters": "Fast | cheap"}],
    "category_breakdown": {"LLMs & Agents": 1},
    "model": "qwen2.5:3b",
}


def test_all_renderers_handle_full_report(current_df, previous_df):
    # Regression: new_trending_repos used to be a list of strings, which crashed the email template.
    results = analyze_trends(current_df, previous_df, topic="machine learning") | {"ai_insights": AI}
    for render in (generate_html, generate_text, generate_markdown):
        out = render(results)
        assert "org/beta" in out
    assert "Agents keep climbing" in generate_email_subject(results)


def test_html_escapes_untrusted_text(current_df, previous_df):
    results = analyze_trends(current_df, previous_df, topic="ml") | {"ai_insights": AI}
    html = generate_html(results)
    assert "<script>" not in html and "&lt;script&gt;" in html
    assert "<b>xss</b>" not in html
    assert "Summary &lt;with&gt; markup." in html


def test_markdown_baseline_note(current_df):
    md = generate_markdown(analyze_trends(current_df, None, topic="ml"))
    assert "baseline run" in md
    assert "AI summary" not in md


def test_markdown_table_pipes_are_escaped(current_df):
    md = generate_markdown(analyze_trends(current_df, None, topic="ml") | {"ai_insights": AI})
    assert "Fast / cheap" in md
