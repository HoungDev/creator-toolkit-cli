import random

from creator_toolkit.title_generator import generate_title


def test_generate_title():
    title = generate_title("python")
    assert "Python" in title


def test_generate_title_empty_keyword():
    assert generate_title("   ") == "Please enter a keyword."


def test_generate_title_with_seeded_rng_is_reproducible():
    first = generate_title("creator workflow", rng=random.Random(2026))
    second = generate_title("creator workflow", rng=random.Random(2026))

    assert first == second


def test_generate_title_with_seeded_rng_preserves_global_random_state():
    state = random.getstate()

    generate_title("creator workflow", rng=random.Random(2026))

    assert random.getstate() == state
