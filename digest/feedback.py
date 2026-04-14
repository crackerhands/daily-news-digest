import json
import os
from typing import Dict

DEPTH_THRESHOLD = 3  # net votes needed to trigger a modifier


def load_prompt_modifier(prefs_path: str = "preferences.json") -> str:
    if not os.path.exists(prefs_path):
        return ""

    with open(prefs_path) as f:
        prefs = json.load(f)

    votes: Dict[str, Dict[str, int]] = prefs.get("votes", {})
    lines = []

    for topic, counts in votes.items():
        net = counts.get("up", 0) - counts.get("down", 0)
        if net >= DEPTH_THRESHOLD:
            lines.append(f"- {topic}: provide more depth and detail than usual")
        elif net <= -DEPTH_THRESHOLD:
            lines.append(f"- {topic}: provide less depth, keep it brief")

    if not lines:
        return ""

    return "User feedback on topic depth (adjust accordingly):\n" + "\n".join(lines)
