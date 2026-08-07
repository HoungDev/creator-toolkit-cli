from creator_toolkit.tag_generator import generate_tags


def test_generate_tags():
    tags = generate_tags()
    assert len(tags) == 5
    assert len(set(tags)) == 5
    assert tags == sorted(tags)


def test_generate_tags_zero():
    assert generate_tags(0) == []


def test_generate_tags_caps_count_to_available_tags():
    assert len(generate_tags(100)) == 10
