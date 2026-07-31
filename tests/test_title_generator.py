from creator_toolkit.title_generator import generate_title


def test_generate_title():
    title = generate_title("python")

    assert isinstance(title, str)
    assert "Python" in title or "python" in title