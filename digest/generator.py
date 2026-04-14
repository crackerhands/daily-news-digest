import json
import re
from typing import Any, Dict, List

import anthropic

MAX_TOKENS_SEARCH = 4000   # Cap for web search turn
MAX_TOKENS_FORMAT = 8000   # Cap for JSON formatting turn

SYSTEM_PROMPT = """You are a daily news digest assistant. Search the web for today's top stories across the requested topic areas."""

JSON_SCHEMA = """{
  "teaser_headline": "The single most interesting story from today's entire digest in one sentence",
  "sections": {
    "football": {
      "summary": "2-3 sentence overview: Fulham + Sunderland results/news, top EPL storylines",
      "deep": "Detailed match reports, tables, transfer news, top club (Arsenal, Man City, Liverpool) updates",
      "feedback_topic": "football"
    },
    "nfl": {
      "summary": "2-3 sentence overview: Jaguars news + top NFL headlines",
      "deep": "Full details on Jaguars moves + broader NFL stories",
      "feedback_topic": "nfl"
    },
    "politics": {
      "stories": [
        {
          "headline": "Story headline",
          "summary": "Neutral 2-sentence factual summary",
          "left_framing": "How left/liberal outlets are framing this story",
          "right_framing": "How right/conservative outlets are framing this story",
          "impact": "Practical impact on everyday Canadians or Americans"
        }
      ],
      "feedback_topic": "politics"
    },
    "investing": {
      "summary": "S&P 500, TSX, key macro events today plus watchlist stocks",
      "deep": "Detailed market analysis, watchlist stock news, upcoming economic events",
      "feedback_topic": "investing"
    },
    "tech": {
      "summary": "2-3 top major tech headlines today",
      "deep": "Full details on each story",
      "feedback_topic": "tech"
    },
    "claude": {
      "summary": "Claude/Anthropic releases, updates, or ecosystem news",
      "deep": "Full details, links to relevant tools or techniques",
      "feedback_topic": "claude"
    },
    "data_engineering": {
      "summary": "Top data engineering + analytics engineering news",
      "deep": "Full details on each item including why it matters",
      "feedback_topic": "data_engineering"
    }
  }
}"""


def _build_search_prompt(watchlist: List[str], prompt_modifier: str, nfl_offseason: bool) -> str:
    nfl_label = "NFL off-season (trades, free agency, draft, training camp)" if nfl_offseason else "NFL (game results, standings, highlights)"
    watchlist_str = ", ".join(watchlist) if watchlist else "general market"
    modifier_section = f"\n\nFeedback adjustments:\n{prompt_modifier}" if prompt_modifier else ""

    return f"""Search the web for today's top news across these topics and gather the information needed:

1. Football: Fulham + Sunderland results/news, top EPL storylines, top clubs (Arsenal, Man City, Liverpool)
2. {nfl_label}: Jaguars news + broader NFL headlines
3. Politics: 2-3 stories covering Canadian politics, American politics, and/or notable world events
4. Investing: S&P 500, TSX, macro events, watchlist stocks: {watchlist_str}
5. Tech: Major tech headlines
6. Claude/Anthropic: releases, ecosystem news (Obsidian plugins, MCP servers, prompt tips, token efficiency)
7. Data engineering: trending GitHub repos, dbt/Spark/Polars/DuckDB updates, job market signals

Search thoroughly for each topic.{modifier_section}"""


def _build_format_prompt(watchlist_str: str) -> str:
    return f"""Now format everything you found into this exact JSON structure. Return ONLY the JSON object — no explanation, no markdown, no other text. Start your response with {{ and end with }}.

Politics must include 2-3 stories with balanced left/right framing — factual, no editorializing.
Investing summary must mention watchlist stocks: {watchlist_str}.

JSON structure:
{JSON_SCHEMA}"""


def generate_digest(
    api_key: str,
    watchlist: List[str],
    prompt_modifier: str,
    nfl_offseason: bool,
) -> Dict[str, Any]:
    client = anthropic.Anthropic(api_key=api_key)
    watchlist_str = ", ".join(watchlist) if watchlist else "general market"

    # Turn 1: search the web
    messages = [{"role": "user", "content": _build_search_prompt(watchlist, prompt_modifier, nfl_offseason)}]
    search_response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=MAX_TOKENS_SEARCH,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
        messages=messages,
    )

    # Turn 2: format as JSON (no tools, forces text-only output)
    messages.append({"role": "assistant", "content": search_response.content})
    messages.append({"role": "user", "content": _build_format_prompt(watchlist_str)})

    format_response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=MAX_TOKENS_FORMAT,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    text_blocks = [block for block in format_response.content if block.type == "text"]
    if not text_blocks:
        raise ValueError("Failed to parse digest JSON: no text block in response")

    raw = text_blocks[-1].text.strip()

    # Strip markdown code fences if present
    raw = re.sub(r"^```json\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse digest JSON: {e}\nRaw response: {raw[:200]}")
