import html
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any, Dict

SECTION_LABELS = {
    "football": "Football (EPL)",
    "nfl": "NFL",
    "politics": "Politics",
    "investing": "Investing",
    "tech": "Tech",
    "claude": "Claude & AI Tools",
    "data_engineering": "Data Engineering",
}

SECTION_ORDER = ["football", "nfl", "politics", "investing", "tech", "claude", "data_engineering"]

STYLES = """
body { font-family: -apple-system, Arial, sans-serif; max-width: 680px; margin: 0 auto; padding: 16px; color: #222; }
h1 { font-size: 22px; border-bottom: 2px solid #eee; padding-bottom: 8px; }
h2 { font-size: 18px; color: #1a1a1a; margin-top: 32px; margin-bottom: 4px; }
h3 { font-size: 15px; margin: 12px 0 4px 0; }
.teaser { font-size: 16px; color: #555; font-style: italic; margin-bottom: 24px; }
.summary { margin-bottom: 8px; }
.deep { background: #f9f9f9; border-left: 3px solid #ddd; padding: 10px 14px; margin: 8px 0 4px 0; font-size: 14px; color: #444; }
.section { border-bottom: 1px solid #eee; padding-bottom: 20px; margin-bottom: 8px; }
.left-frame { background: #f0f4ff; border-left: 3px solid #1a73e8; padding: 8px 12px; margin: 6px 0; font-size: 14px; }
.right-frame { background: #fff4f4; border-left: 3px solid #c0392b; padding: 8px 12px; margin: 6px 0; font-size: 14px; }
.frame-label { font-size: 12px; font-weight: bold; margin-bottom: 4px; }
.impact { font-size: 14px; color: #333; margin: 6px 0; }
.story { margin-bottom: 16px; }
"""


def _esc(text: str) -> str:
    return html.escape(str(text))


def _build_standard_section(key: str, section: Dict) -> str:
    label = SECTION_LABELS.get(key, key.title())
    summary = _esc(section.get("summary", ""))
    deep = _esc(section.get("deep", ""))
    return f"""
<div class="section">
  <h2>{label}</h2>
  <p class="summary">{summary}</p>
  <div class="deep">{deep}</div>
</div>"""


def _build_politics_section(section: Dict) -> str:
    stories_html = ""
    for story in section.get("stories", []):
        headline = _esc(story.get("headline", ""))
        summary = _esc(story.get("summary", ""))
        left = _esc(story.get("left_framing", ""))
        right = _esc(story.get("right_framing", ""))
        impact = _esc(story.get("impact", ""))
        stories_html += f"""
  <div class="story">
    <h3>{headline}</h3>
    <p class="summary">{summary}</p>
    <p class="impact"><strong>Impact:</strong> {impact}</p>
    <div class="left-frame"><div class="frame-label">Liberal framing</div>{left}</div>
    <div class="right-frame"><div class="frame-label">Conservative framing</div>{right}</div>
  </div>"""

    return f"""
<div class="section">
  <h2>Politics</h2>
  {stories_html}
</div>"""


def _build_html(digest: Dict, date: str) -> str:
    teaser = _esc(digest.get("teaser_headline", "Your daily digest is ready"))
    sections_html = ""
    for key in SECTION_ORDER:
        section = digest["sections"].get(key)
        if not section:
            continue
        if key == "politics":
            sections_html += _build_politics_section(section)
        else:
            sections_html += _build_standard_section(key, section)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>{STYLES}</style>
</head>
<body>
<h1>Daily Digest &mdash; {date}</h1>
<p class="teaser">{teaser}</p>
{sections_html}
</body>
</html>"""


def build_email(
    digest: Dict[str, Any],
    from_addr: str,
    to_addr: str,
    date: str,
) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Digest \u2014 {date}"
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg.attach(MIMEText(_build_html(digest, date), "html", "utf-8"))
    return msg
