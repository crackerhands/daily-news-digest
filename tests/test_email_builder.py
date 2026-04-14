import pytest
from digest.email_builder import build_email


SAMPLE_DIGEST = {
    "teaser_headline": "Fulham clinch Europa League spot",
    "sections": {
        "football": {
            "summary": "Fulham beat Chelsea 2-0.",
            "deep": "Full match report.",
            "feedback_topic": "football"
        },
        "nfl": {
            "summary": "Jaguars sign QB.",
            "deep": "Full details.",
            "feedback_topic": "nfl"
        },
        "politics": {
            "stories": [
                {
                    "headline": "Budget passed",
                    "summary": "Parliament passed budget.",
                    "left_framing": "Historic investment.",
                    "right_framing": "Reckless spending.",
                    "impact": "Taxes rise slightly."
                }
            ],
            "feedback_topic": "politics"
        },
        "investing": {
            "summary": "ATZ.TO up 3%.",
            "deep": "Strong earnings.",
            "feedback_topic": "investing"
        },
        "tech": {
            "summary": "GPT-5 released.",
            "deep": "Full breakdown.",
            "feedback_topic": "tech"
        },
        "claude": {
            "summary": "New MCP server released.",
            "deep": "Full details.",
            "feedback_topic": "claude"
        },
        "data_engineering": {
            "summary": "dbt 2.0 released.",
            "deep": "Full changelog.",
            "feedback_topic": "data_engineering"
        }
    }
}

DATE = "2026-04-13"
FEEDBACK_BASE = "https://crackerhands.github.io/daily-news-digest"


def test_build_email_returns_mime_message():
    msg = build_email(
        digest=SAMPLE_DIGEST,
        from_addr="test@gmail.com",
        to_addr="test@gmail.com",
        date=DATE,
        feedback_base_url=FEEDBACK_BASE,
    )
    assert msg["Subject"] == f"Daily Digest — {DATE}"
    assert msg["From"] == "test@gmail.com"
    assert msg["To"] == "test@gmail.com"


def test_build_email_contains_amp_part():
    msg = build_email(
        digest=SAMPLE_DIGEST,
        from_addr="test@gmail.com",
        to_addr="test@gmail.com",
        date=DATE,
        feedback_base_url=FEEDBACK_BASE,
    )
    content_types = [part.get_content_type() for part in msg.walk()]
    assert "text/x-amp-html" in content_types


def test_build_email_contains_html_fallback():
    msg = build_email(
        digest=SAMPLE_DIGEST,
        from_addr="test@gmail.com",
        to_addr="test@gmail.com",
        date=DATE,
        feedback_base_url=FEEDBACK_BASE,
    )
    content_types = [part.get_content_type() for part in msg.walk()]
    assert "text/html" in content_types


def test_amp_part_contains_summary_and_feedback_buttons():
    msg = build_email(
        digest=SAMPLE_DIGEST,
        from_addr="test@gmail.com",
        to_addr="test@gmail.com",
        date=DATE,
        feedback_base_url=FEEDBACK_BASE,
    )
    for part in msg.walk():
        if part.get_content_type() == "text/x-amp-html":
            body = part.get_payload(decode=True).decode()
            assert "Fulham beat Chelsea 2-0." in body
            assert "vote=up" in body
            assert "vote=down" in body
            break
    else:
        pytest.fail("No AMP part found")


def test_politics_section_has_framing_in_amp():
    msg = build_email(
        digest=SAMPLE_DIGEST,
        from_addr="test@gmail.com",
        to_addr="test@gmail.com",
        date=DATE,
        feedback_base_url=FEEDBACK_BASE,
    )
    for part in msg.walk():
        if part.get_content_type() == "text/x-amp-html":
            body = part.get_payload(decode=True).decode()
            assert "Historic investment." in body
            assert "Reckless spending." in body
            break
