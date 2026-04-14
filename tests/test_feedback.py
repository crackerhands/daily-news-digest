import json
import pytest
from digest.feedback import load_prompt_modifier


def test_no_votes_returns_neutral_modifier(tmp_path):
    prefs = tmp_path / "preferences.json"
    prefs.write_text(json.dumps({
        "votes": {
            "football": {"up": 0, "down": 0},
            "nfl": {"up": 0, "down": 0}
        }
    }))
    modifier = load_prompt_modifier(str(prefs))
    assert modifier == ""


def test_upvoted_topic_requests_more_depth(tmp_path):
    prefs = tmp_path / "preferences.json"
    prefs.write_text(json.dumps({
        "votes": {
            "football": {"up": 5, "down": 0},
            "nfl": {"up": 0, "down": 0}
        }
    }))
    modifier = load_prompt_modifier(str(prefs))
    assert "football" in modifier
    assert "more depth" in modifier.lower()


def test_downvoted_topic_requests_less_depth(tmp_path):
    prefs = tmp_path / "preferences.json"
    prefs.write_text(json.dumps({
        "votes": {
            "football": {"up": 0, "down": 4},
            "nfl": {"up": 0, "down": 0}
        }
    }))
    modifier = load_prompt_modifier(str(prefs))
    assert "football" in modifier
    assert "less depth" in modifier.lower()


def test_missing_prefs_file_returns_empty_string():
    modifier = load_prompt_modifier("/nonexistent/preferences.json")
    assert modifier == ""
