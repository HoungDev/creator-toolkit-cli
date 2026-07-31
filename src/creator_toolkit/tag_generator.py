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
    """Generate random tags."""
    return sample(DEFAULT_TAGS, k=min(count, len(DEFAULT_TAGS)))