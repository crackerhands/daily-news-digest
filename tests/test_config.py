import json
import os
import pytest
from digest.config import Config


def test_config_loads_email(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "email": {"address": "test@gmail.com"},
        "watchlist": ["ATZ.TO"],
        "topics": {
            "football": True, "nfl": True, "politics": True,
            "investing": True, "tech": True, "claude": True,
            "data_engineering": True
        },
        "nfl_offseason": True
    }))
    os.environ["CLAUDE_API_KEY"] = "test-key"
    os.environ["GMAIL_APP_PASSWORD"] = "test-pass"
    config = Config.load(str(cfg_file))
    assert config.email_address == "test@gmail.com"
    assert config.watchlist == ["ATZ.TO"]
    assert config.claude_api_key == "test-key"
    assert config.gmail_app_password == "test-pass"
    assert config.topics["football"] is True


def test_config_missing_api_key_raises(tmp_path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "email": {"address": "test@gmail.com"},
        "watchlist": [],
        "topics": {},
        "nfl_offseason": False
    }))
    os.environ.pop("CLAUDE_API_KEY", None)
    with pytest.raises(EnvironmentError, match="CLAUDE_API_KEY"):
        Config.load(str(cfg_file))
