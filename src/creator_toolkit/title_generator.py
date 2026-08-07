from random import Random, choice

TEMPLATES = [
    "10 {keyword} Tips Every Beginner Should Know",
    "The Ultimate Guide to {keyword}",
    "How to Master {keyword}",
    "{keyword}: A Complete Beginner's Guide",
    "Everything You Need to Know About {keyword}",
]


def generate_title(keyword: str, *, rng: Random | None = None) -> str:
    """Generate a title from a keyword."""
    if not keyword.strip():
        return "Please enter a keyword."

    chooser = choice if rng is None else rng.choice
    return chooser(TEMPLATES).format(keyword=keyword.title())
