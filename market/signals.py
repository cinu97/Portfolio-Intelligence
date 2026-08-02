"""Signal generation utilities."""


def generate_signal(score: float) -> str:
    """Map a numeric score to a simple signal label."""
    if score > 0:
        return "buy"
    if score < 0:
        return "sell"
    return "hold"
