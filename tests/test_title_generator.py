from creator_toolkit.title_generator import generate_title


def test_generate_title():
    title = generate_title("python")

    assert isinstance(title, str)
    assert "Python" in title or "python" in title
    assert len(title) > 0
def test_generate_title_empty_keyword():
    assert generate_title("") == "Please enter a keyword."    