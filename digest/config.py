import json
import os
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Config:
    email_address: str
    watchlist: List[str]
    topics: Dict[str, bool]
    nfl_offseason: bool
    claude_api_key: str
    gmail_app_password: str

    @classmethod
    def load(cls, config_path: str = "config.json") -> "Config":
        with open(config_path) as f:
            data = json.load(f)

        claude_api_key = os.environ.get("CLAUDE_API_KEY")
        if not claude_api_key:
            raise EnvironmentError("CLAUDE_API_KEY environment variable is not set")

        gmail_app_password = os.environ.get("GMAIL_APP_PASSWORD")
        if not gmail_app_password:
            raise EnvironmentError("GMAIL_APP_PASSWORD environment variable is not set")

        return cls(
            email_address=data["email"]["address"],
            watchlist=data.get("watchlist", []),
            topics=data.get("topics", {}),
            nfl_offseason=data.get("nfl_offseason", True),
            claude_api_key=claude_api_key,
            gmail_app_password=gmail_app_password,
        )
