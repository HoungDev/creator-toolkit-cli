from random import sample

DEFAULT_TAGS = [
    "python",
    "automation",
    "ai",
    "programming",
    "developer",
    "tutorial",
    "coding",
    "opensource",
    "github",
    "productivity",
]


def generate_tags(count: int = 5) -> list[str]:
    """Return up to ``count`` unique tags in alphabetical order."""
    if count <= 0:
        return []

    tags = sample(DEFAULT_TAGS, k=min(count, len(DEFAULT_TAGS)))
    return sorted(tags)
