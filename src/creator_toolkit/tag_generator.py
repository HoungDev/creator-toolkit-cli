from random import Random, sample

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


def generate_tags(count: int = 5, *, rng: Random | None = None) -> list[str]:
    """Return up to ``count`` unique tags in alphabetical order."""
    if count <= 0:
        return []

    sampler = sample if rng is None else rng.sample
    tags = sampler(DEFAULT_TAGS, k=min(count, len(DEFAULT_TAGS)))
    return sorted(tags)
