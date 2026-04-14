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


def _esc(text: str) -> str:
    return html.escape(str(text))


def _feedback_buttons(topic: str, date: str, base_url: str) -> str:
    up_url = f"{base_url}?topic={topic}&vote=up&date={date}"
    down_url = f"{base_url}?topic={topic}&vote=down&date={date}"
    return (
        f'<a href="{up_url}" style="margin-right:8px;">👍 More like this</a>'
        f'<a href="{down_url}">👎 Less of this</a>'
    )


def _build_amp_standard_section(key: str, section: Dict, date: str, base_url: str) -> str:
    label = SECTION_LABELS.get(key, key.title())
    summary = _esc(section.get("summary", ""))
    deep = _esc(section.get("deep", ""))
    buttons = _feedback_buttons(key, date, base_url)
    return f"""
  <div style="margin-bottom:24px;border-bottom:1px solid #eee;padding-bottom:16px;">
    <h2 style="font-size:18px;margin-bottom:8px;">{label}</h2>
    <p>{summary}</p>
    <amp-accordion animate>
      <section>
        <h3 style="font-size:14px;color:#555;">Read more &darr;</h3>
        <div style="padding:8px 0;">{deep}</div>
      </section>
    </amp-accordion>
    <p style="margin-top:8px;font-size:12px;">{buttons}</p>
  </div>"""


def _build_amp_politics_section(section: Dict, date: str, base_url: str) -> str:
    stories_html = ""
    for story in section.get("stories", []):
        headline = _esc(story.get("headline", ""))
        summary = _esc(story.get("summary", ""))
        left = _esc(story.get("left_framing", ""))
        right = _esc(story.get("right_framing", ""))
        impact = _esc(story.get("impact", ""))
        stories_html += f"""
    <div style="margin-bottom:16px;">
      <h3 style="font-size:15px;">{headline}</h3>
      <p>{summary}</p>
      <p><strong>Impact:</strong> {impact}</p>
      <amp-accordion animate>
        <section>
          <h4 style="font-size:13px;color:#1a73e8;">Liberal framing &darr;</h4>
          <div style="padding:8px;background:#f0f4ff;">{left}</div>
        </section>
        <section>
          <h4 style="font-size:13px;color:#c0392b;">Conservative framing &darr;</h4>
          <div style="padding:8px;background:#fff4f4;">{right}</div>
        </section>
      </amp-accordion>
    </div>"""

    buttons = _feedback_buttons("politics", date, base_url)
    return f"""
  <div style="margin-bottom:24px;border-bottom:1px solid #eee;padding-bottom:16px;">
    <h2 style="font-size:18px;margin-bottom:8px;">Politics</h2>
    {stories_html}
    <p style="font-size:12px;">{buttons}</p>
  </div>"""


def _build_amp_body(digest: Dict, date: str, base_url: str) -> str:
    teaser = _esc(digest.get("teaser_headline", "Your daily digest is ready"))
    sections_html = ""
    for key in SECTION_ORDER:
        section = digest["sections"].get(key)
        if not section:
            continue
        if key == "politics":
            sections_html += _build_amp_politics_section(section, date, base_url)
        else:
            sections_html += _build_amp_standard_section(key, section, date, base_url)

    return f"""<!doctype html>
<html ⚡4email data-css-strict>
<head>
  <meta charset="utf-8">
  <style amp4email-boilerplate>body{{visibility:hidden}}</style>
  <script async src="https://cdn.ampproject.org/v0.js"></script>
  <script async custom-element="amp-accordion" src="https://cdn.ampproject.org/v0/amp-accordion-0.1.js"></script>
  <style amp-custom>
    body {{ font-family: -apple-system, Arial, sans-serif; max-width: 680px; margin: 0 auto; padding: 16px; color: #222; }}
    h1 {{ font-size: 22px; }}
    h2 {{ color: #1a1a1a; }}
    amp-accordion section {{ border: 1px solid #ddd; border-radius: 4px; margin: 4px 0; }}
    amp-accordion h3, amp-accordion h4 {{ padding: 8px 12px; margin: 0; cursor: pointer; background: #f9f9f9; }}
  </style>
</head>
<body>
  <h1>Daily Digest — {date}</h1>
  <p style="font-size:16px;color:#555;margin-bottom:24px;"><em>{teaser}</em></p>
  {sections_html}
</body>
</html>"""


def _build_html_fallback(digest: Dict, date: str, base_url: str) -> str:
    teaser = _esc(digest.get("teaser_headline", "Your daily digest is ready"))
    sections_html = ""
    for key in SECTION_ORDER:
        section = digest["sections"].get(key)
        if not section:
            continue
        label = SECTION_LABELS.get(key, key.title())
        if key == "politics":
            stories_html = ""
            for story in section.get("stories", []):
                stories_html += f"""
        <div style="margin-bottom:12px;">
          <h3>{_esc(story.get('headline',''))}</h3>
          <p>{_esc(story.get('summary',''))}</p>
          <p><strong>Impact:</strong> {_esc(story.get('impact',''))}</p>
          <details><summary style="color:#1a73e8;">Liberal framing</summary><p>{_esc(story.get('left_framing',''))}</p></details>
          <details><summary style="color:#c0392b;">Conservative framing</summary><p>{_esc(story.get('right_framing',''))}</p></details>
        </div>"""
            buttons = _feedback_buttons(key, date, base_url)
            sections_html += f"<div><h2>{label}</h2>{stories_html}<p>{buttons}</p></div><hr>"
        else:
            summary = _esc(section.get("summary", ""))
            deep = _esc(section.get("deep", ""))
            buttons = _feedback_buttons(key, date, base_url)
            sections_html += f"""
      <div>
        <h2>{label}</h2>
        <p>{summary}</p>
        <details><summary>Read more</summary><p>{deep}</p></details>
        <p>{buttons}</p>
      </div><hr>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>body{{font-family:-apple-system,Arial,sans-serif;max-width:680px;margin:0 auto;padding:16px;}}</style>
</head><body>
<h1>Daily Digest — {date}</h1>
<p><em>{teaser}</em></p>
{sections_html}
</body></html>"""


def build_email(
    digest: Dict[str, Any],
    from_addr: str,
    to_addr: str,
    date: str,
    feedback_base_url: str,
) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"Daily Digest — {date}"
    msg["From"] = from_addr
    msg["To"] = to_addr

    html_part = MIMEText(_build_html_fallback(digest, date, feedback_base_url), "html", "utf-8")
    amp_part = MIMEText(_build_amp_body(digest, date, feedback_base_url), "x-amp-html", "utf-8")

    # Order: html first (fallback), amp last (preferred by Gmail)
    msg.attach(html_part)
    msg.attach(amp_part)
    return msg
