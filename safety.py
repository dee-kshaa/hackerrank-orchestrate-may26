"""Safety and escalation module."""

from typing import Tuple


HIGH_RISK_KEYWORDS = [
    "lawsuit",
    "legal",
    "fraud",
    "scam",
    "hack",
    "breach",
    "stolen",
    "threat",
    "urgent",
    "escalate"
]


def check_safety(text: str) -> Tuple[bool, str]:

    lower_text = text.lower()

    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in lower_text:
            return False, f"High-risk keyword detected: {keyword}"

    return True, "Safe"


def should_escalate(text: str) -> bool:

    is_safe, _ = check_safety(text)

    return not is_safe