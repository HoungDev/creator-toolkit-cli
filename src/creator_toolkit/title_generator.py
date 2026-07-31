from random import choice

TEMPLATES = [
    "10 {keyword} Tips Every Beginner Should Know",
    "The Ultimate Guide to {keyword}",
    "How to Master {keyword}",
    "{keyword}: A Complete Beginner's Guide",
    "Everything You Need to Know About {keyword}",
]


def generate_title(keyword: str) -> str:
    return choice(TEMPLATES).format(keyword=keyword.title())