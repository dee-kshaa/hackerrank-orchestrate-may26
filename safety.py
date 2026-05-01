"""Safety and escalation module."""


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


def check_safety(text, config=None):

    lower_text = str(text).lower()

    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in lower_text:
            return {
                "safe": False,
                "risk_level": "high",
                "reason": f"High-risk keyword detected: {keyword}"
            }

    return {
        "safe": True,
        "risk_level": "low",
        "reason": "Safe"
    }


def should_escalate(text, config=None):

    result = check_safety(text)

    return not result["safe"]