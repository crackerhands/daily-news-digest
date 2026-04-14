import json
import re
from typing import Any, Dict, List

import anthropic

MAX_TOKENS = 4000  # Hard cap per run to control cost

SYSTEM_PROMPT = """You are a daily news digest assistant. Your job is to search the web for today's top stories across several topic areas and return a structured JSON digest.

Always return ONLY valid JSON matching the exact schema provided. No markdown, no explanation, just the JSON object."""


def _build_prompt(watchlist: List[str], prompt_modifier: str, nfl_offseason: bool) -> str:
    nfl_label = "NFL off-season (trades, free agency, draft, training camp)" if nfl_offseason else "NFL (game results, standings, highlights)"
    watchlist_str = ", ".join(watchlist) if watchlist else "general market"

    modifier_section = f"\n\nFeedback adjustments:\n{prompt_modifier}" if prompt_modifier else ""

    return f"""Search the web and generate today's news digest. Return a single JSON object with this exact structure:

{{
  "teaser_headline": "The single most interesting story from today's entire digest in one sentence",
  "sections": {{
    "football": {{
      "summary": "2-3 sentence overview: Fulham + Sunderland results/news, top EPL storylines",
      "deep": "Detailed match reports, tables, transfer news, top club (Arsenal, Man City, Liverpool) updates",
      "feedback_topic": "football"
    }},
    "nfl": {{
      "summary": "2-3 sentence overview: Jaguars news + top {nfl_label} headlines",
      "deep": "Full details on Jaguars moves + broader NFL stories",
      "feedback_topic": "nfl"
    }},
    "politics": {{
      "stories": [
        {{
          "headline": "Story headline",
          "summary": "Neutral 2-sentence factual summary",
          "left_framing": "How left/liberal outlets are framing this story",
          "right_framing": "How right/conservative outlets are framing this story",
          "impact": "Practical impact on everyday Canadians or Americans"
        }}
      ],
      "feedback_topic": "politics"
    }},
    "investing": {{
      "summary": "S&P 500, TSX, key macro events today. Watchlist: {watchlist_str}",
      "deep": "Detailed market analysis, watchlist stock news, upcoming economic events",
      "feedback_topic": "investing"
    }},
    "tech": {{
      "summary": "2-3 top major tech headlines today",
      "deep": "Full details on each story",
      "feedback_topic": "tech"
    }},
    "claude": {{
      "summary": "Claude/Anthropic releases, updates, or ecosystem news (Obsidian plugins, MCP servers, prompt tips, token efficiency)",
      "deep": "Full details, links to relevant tools or techniques",
      "feedback_topic": "claude"
    }},
    "data_engineering": {{
      "summary": "Top data engineering + analytics engineering news: trending GitHub repos, dbt/Spark/Polars/DuckDB updates, job market signals",
      "deep": "Full details on each item including why it matters",
      "feedback_topic": "data_engineering"
    }}
  }}
}}

Politics section must include 2-3 stories covering Canadian politics, American politics, and/or notable world events. Keep left/right framing factual and balanced — do not editorialize.{modifier_section}"""


def generate_digest(
    api_key: str,
    watchlist: List[str],
    prompt_modifier: str,
    nfl_offseason: bool,
) -> Dict[str, Any]:
    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 10}],
        messages=[{"role": "user", "content": _build_prompt(watchlist, prompt_modifier, nfl_offseason)}],
    )

    # Extract the final text block (after any tool use)
    text_blocks = [block for block in response.content if block.type == "text"]
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
