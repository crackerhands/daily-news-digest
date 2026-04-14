import json
import pytest
from unittest.mock import MagicMock, patch
from digest.generator import generate_digest


def _make_mock_response(content: str):
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = content
    mock_response = MagicMock()
    mock_response.content = [mock_block]
    return mock_response


SAMPLE_JSON = json.dumps({
    "teaser_headline": "Fulham clinch Europa League spot",
    "sections": {
        "football": {
            "summary": "Fulham beat Chelsea 2-0.",
            "deep": "Full match report here.",
            "feedback_topic": "football"
        },
        "nfl": {
            "summary": "Jaguars sign new QB.",
            "deep": "Full details here.",
            "feedback_topic": "nfl"
        },
        "politics": {
            "stories": [
                {
                    "headline": "Budget passed",
                    "summary": "Parliament passed a budget.",
                    "left_framing": "Historic investment.",
                    "right_framing": "Reckless spending.",
                    "impact": "Taxes rise slightly."
                }
            ],
            "feedback_topic": "politics"
        },
        "investing": {
            "summary": "ATZ.TO up 3%.",
            "deep": "Aritzia reports strong earnings.",
            "feedback_topic": "investing"
        },
        "tech": {
            "summary": "OpenAI releases GPT-5.",
            "deep": "Full breakdown.",
            "feedback_topic": "tech"
        },
        "claude": {
            "summary": "Claude gains new tool use.",
            "deep": "Full details.",
            "feedback_topic": "claude"
        },
        "data_engineering": {
            "summary": "dbt 2.0 released.",
            "deep": "Full changelog.",
            "feedback_topic": "data_engineering"
        }
    }
})


@patch("digest.generator.anthropic.Anthropic")
def test_generate_digest_returns_structured_output(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response(SAMPLE_JSON)

    result = generate_digest(
        api_key="test-key",
        watchlist=["ATZ.TO"],
        prompt_modifier="",
        nfl_offseason=True
    )

    assert result["teaser_headline"] == "Fulham clinch Europa League spot"
    assert "football" in result["sections"]
    assert result["sections"]["football"]["summary"] == "Fulham beat Chelsea 2-0."
    assert len(result["sections"]["politics"]["stories"]) == 1
    assert result["sections"]["politics"]["stories"][0]["left_framing"] == "Historic investment."


@patch("digest.generator.anthropic.Anthropic")
def test_generate_digest_raises_on_invalid_json(mock_anthropic_cls):
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client
    mock_client.messages.create.return_value = _make_mock_response("not json at all")

    with pytest.raises(ValueError, match="Failed to parse digest JSON"):
        generate_digest(
            api_key="test-key",
            watchlist=["ATZ.TO"],
            prompt_modifier="",
            nfl_offseason=True
        )
