import smtplib
import ssl
from datetime import date
from email.mime.multipart import MIMEMultipart

from digest.config import Config
from digest.email_builder import build_email
from digest.feedback import load_prompt_modifier
from digest.generator import generate_digest

FEEDBACK_BASE_URL = "https://crackerhands.github.io/daily-news-digest"


def send_email(msg: MIMEMultipart, from_addr: str, app_password: str) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(from_addr, app_password)
        server.send_message(msg)


def main() -> None:
    config = Config.load("config.json")
    today = date.today().isoformat()

    prompt_modifier = load_prompt_modifier("preferences.json")

    print(f"Generating digest for {today}...")
    digest = generate_digest(
        api_key=config.claude_api_key,
        watchlist=config.watchlist,
        prompt_modifier=prompt_modifier,
        nfl_offseason=config.nfl_offseason,
    )

    print(f"Top story: {digest['teaser_headline']}")

    msg = build_email(
        digest=digest,
        from_addr=config.email_address,
        to_addr=config.email_address,
        date=today,
        feedback_base_url=FEEDBACK_BASE_URL,
    )

    print("Sending email...")
    send_email(msg, config.email_address, config.gmail_app_password)
    print("Done.")


if __name__ == "__main__":
    main()
