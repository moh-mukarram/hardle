"""
Rank derivation — pure function, no DB, no caching.
Rank is ALWAYS computed at read-time from total_points.
"""

RANK_THRESHOLDS = [
    (10000, "Diamond"),
    (5000, "Platinum"),
    (2500, "Gold"),
    (1000, "Silver"),
    (0, "Bronze"),
]


def get_rank(total_points: int) -> str:
    """Return the rank name for a given point total."""
    for threshold, rank in RANK_THRESHOLDS:
        if total_points >= threshold:
            return rank
    return "Bronze"
