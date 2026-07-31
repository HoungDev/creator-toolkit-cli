from creator_toolkit.tag_generator import generate_tags


def test_generate_tags():
    tags = generate_tags()

    assert isinstance(tags, list)
    assert len(tags) == 5