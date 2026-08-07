import pytest

from creator_toolkit.rename_images import rename_images


def test_rename_images_empty_folder(tmp_path):
    assert rename_images(tmp_path) == []


def test_rename_images_supported_files_in_stable_order(tmp_path):
    (tmp_path / "z.PNG").write_bytes(b"z")
    (tmp_path / "a.jpg").write_bytes(b"a")
    (tmp_path / "notes.txt").write_text("keep", encoding="utf-8")
    renamed = rename_images(tmp_path)
    assert [(source.name, destination.name) for source, destination in renamed] == [
        ("a.jpg", "image_1.jpg"),
        ("z.PNG", "image_2.png"),
    ]
    assert (tmp_path / "image_1.jpg").read_bytes() == b"a"
    assert (tmp_path / "image_2.png").read_bytes() == b"z"
    assert (tmp_path / "notes.txt").read_text(encoding="utf-8") == "keep"


def test_rename_images_handles_existing_numbered_names(tmp_path):
    (tmp_path / "image_1.jpg").write_bytes(b"first")
    (tmp_path / "other.jpg").write_bytes(b"second")
    rename_images(tmp_path)
    assert (tmp_path / "image_1.jpg").read_bytes() == b"first"
    assert (tmp_path / "image_2.jpg").read_bytes() == b"second"


def test_rename_images_rejects_missing_folder(tmp_path):
    with pytest.raises(FileNotFoundError, match="Folder not found"):
        rename_images(tmp_path / "missing")


def test_rename_images_rejects_file(tmp_path):
    file_path = tmp_path / "image.jpg"
    file_path.write_bytes(b"image")
    with pytest.raises(NotADirectoryError, match="Not a directory"):
        rename_images(file_path)
