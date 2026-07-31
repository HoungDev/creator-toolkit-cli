from pathlib import Path

from creator_toolkit.rename_images import rename_images


def test_rename_images_empty_folder(tmp_path):
    rename_images(str(tmp_path))

    assert list(tmp_path.glob("*.jpg")) == []
    assert list(tmp_path.glob("*.png")) == []