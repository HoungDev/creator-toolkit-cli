from creator_toolkit.title_generator import generate_title


def test_generate_title():
    title = generate_title("python")
    assert "Python" in title


def test_generate_title_empty_keyword():
    assert generate_title("   ") == "Please enter a keyword."
