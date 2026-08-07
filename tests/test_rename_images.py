import json
from pathlib import Path

import pytest

from creator_toolkit.rename_images import (
    InvalidPrefixError,
    ManifestError,
    plan_image_renames,
    rename_images,
    undo_renames,
)


def test_rename_images_empty_folder(tmp_path):
    assert plan_image_renames(tmp_path) == []
    assert rename_images(tmp_path) == []


def test_dry_run_returns_plan_without_changing_files(tmp_path):
    image = tmp_path / "photo.JPG"
    image.write_bytes(b"photo")

    operations = rename_images(tmp_path, dry_run=True)

    assert [(source.name, destination.name) for source, destination in operations] == [
        ("photo.JPG", "image_1.jpg")
    ]
    assert image.read_bytes() == b"photo"
    assert not (tmp_path / "image_1.jpg").exists()


def test_dry_run_supports_a_custom_prefix_without_changing_files(tmp_path):
    image = tmp_path / "photo.JPG"
    image.write_bytes(b"photo")

    operations = rename_images(tmp_path, dry_run=True, prefix="campaign")

    assert [(source.name, destination.name) for source, destination in operations] == [
        ("photo.JPG", "campaign_1.jpg")
    ]
    assert image.read_bytes() == b"photo"
    assert not (tmp_path / "campaign_1.jpg").exists()


def test_rename_images_writes_manifest_and_undoes(tmp_path):
    (tmp_path / "z.PNG").write_bytes(b"z")
    (tmp_path / "a.jpg").write_bytes(b"a")
    (tmp_path / "notes.txt").write_text("keep", encoding="utf-8")
    manifest = tmp_path / "rename-manifest.json"

    renamed = rename_images(tmp_path, manifest_path=manifest)

    assert [(source.name, destination.name) for source, destination in renamed] == [
        ("a.jpg", "image_1.jpg"),
        ("z.PNG", "image_2.png"),
    ]
    assert (tmp_path / "image_1.jpg").read_bytes() == b"a"
    assert (tmp_path / "image_2.png").read_bytes() == b"z"
    assert (tmp_path / "notes.txt").read_text(encoding="utf-8") == "keep"
    assert json.loads(manifest.read_text(encoding="utf-8"))["status"] == "applied"

    restored = undo_renames(manifest)

    assert [(source.name, destination.name) for source, destination in restored] == [
        ("image_1.jpg", "a.jpg"),
        ("image_2.png", "z.PNG"),
    ]
    assert (tmp_path / "a.jpg").read_bytes() == b"a"
    assert (tmp_path / "z.PNG").read_bytes() == b"z"
    assert json.loads(manifest.read_text(encoding="utf-8"))["status"] == "undone"


def test_custom_prefix_manifest_undoes_without_prefix_argument(tmp_path):
    (tmp_path / "photo.jpg").write_bytes(b"photo")
    manifest = tmp_path / "rename-manifest.json"

    rename_images(tmp_path, manifest_path=manifest, prefix="campaign")

    assert (tmp_path / "campaign_1.jpg").read_bytes() == b"photo"
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["version"] == 1
    assert payload["operations"] == [{"source": "photo.jpg", "destination": "campaign_1.jpg"}]

    undo_renames(manifest)

    assert (tmp_path / "photo.jpg").read_bytes() == b"photo"
    assert not (tmp_path / "campaign_1.jpg").exists()


def test_custom_prefix_collision_is_detected_before_changes(tmp_path):
    image = tmp_path / "photo.jpg"
    image.write_bytes(b"photo")
    (tmp_path / "campaign_1.jpg").mkdir()

    with pytest.raises(FileExistsError, match="Destination already exists"):
        rename_images(tmp_path, prefix="campaign")

    assert image.read_bytes() == b"photo"
    assert (tmp_path / "campaign_1.jpg").is_dir()


@pytest.mark.parametrize(
    "prefix",
    [
        "",
        "   ",
        " campaign",
        "campaign ",
        ".",
        "..",
        "folder/campaign",
        "folder\\campaign",
        "campaign:",
        'campaign"',
        "campaign|",
        "campaign?",
        "campaign*",
        "campaign.",
        "campaign\x00",
        "CON",
        "con.txt",
        "PRN",
        "AUX",
        "NUL",
        "COM1",
        "LPT9",
        "a" * 256,
    ],
)
def test_invalid_prefixes_fail_before_file_or_manifest_changes(tmp_path, prefix):
    image = tmp_path / "photo.jpg"
    image.write_bytes(b"photo")
    manifest = tmp_path / "manifest.json"

    with pytest.raises(InvalidPrefixError, match="Prefix"):
        rename_images(tmp_path, prefix=prefix, manifest_path=manifest)

    assert image.read_bytes() == b"photo"
    assert not manifest.exists()


def test_unicode_prefix_is_supported_cross_platform(tmp_path):
    image = tmp_path / "photo.PNG"
    image.write_bytes(b"photo")

    operations = plan_image_renames(tmp_path, prefix="chiến-dịch")

    assert operations[0][1].name == "chiến-dịch_1.png"


def test_prefix_must_leave_room_for_generated_filename_suffix(tmp_path):
    image = tmp_path / "photo.jpeg"
    image.write_bytes(b"photo")

    with pytest.raises(InvalidPrefixError, match="Generated filename"):
        plan_image_renames(tmp_path, prefix="a" * 250)

    assert image.read_bytes() == b"photo"


def test_rename_images_handles_existing_numbered_names(tmp_path):
    (tmp_path / "image_1.jpg").write_bytes(b"first")
    (tmp_path / "other.jpg").write_bytes(b"second")

    rename_images(tmp_path)

    assert (tmp_path / "image_1.jpg").read_bytes() == b"first"
    assert (tmp_path / "image_2.jpg").read_bytes() == b"second"


def test_rename_images_rolls_back_finalize_failure(tmp_path, monkeypatch):
    (tmp_path / "a.jpg").write_bytes(b"a")
    (tmp_path / "z.jpg").write_bytes(b"z")
    original_rename = Path.rename
    calls = 0

    def fail_second_finalize(path, target):
        nonlocal calls
        calls += 1
        if calls == 4:
            raise OSError("simulated rename failure")
        return original_rename(path, target)

    monkeypatch.setattr(Path, "rename", fail_second_finalize)

    with pytest.raises(OSError, match="simulated rename failure"):
        rename_images(tmp_path)

    assert (tmp_path / "a.jpg").read_bytes() == b"a"
    assert (tmp_path / "z.jpg").read_bytes() == b"z"
    assert not list(tmp_path.glob(".creator-toolkit-*.tmp"))


def test_rename_images_restores_files_after_staging_failure(tmp_path, monkeypatch):
    (tmp_path / "a.jpg").write_bytes(b"a")
    (tmp_path / "z.jpg").write_bytes(b"z")
    original_rename = Path.rename
    calls = 0

    def fail_second_stage(path, target):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated staging failure")
        return original_rename(path, target)

    monkeypatch.setattr(Path, "rename", fail_second_stage)

    with pytest.raises(OSError, match="simulated staging failure"):
        rename_images(tmp_path)

    assert (tmp_path / "a.jpg").read_bytes() == b"a"
    assert (tmp_path / "z.jpg").read_bytes() == b"z"
    assert not list(tmp_path.glob(".creator-toolkit-*.tmp"))


def test_manifest_collision_blocks_undo(tmp_path):
    (tmp_path / "photo.jpg").write_bytes(b"original")
    manifest = tmp_path / "rename-manifest.json"
    rename_images(tmp_path, manifest_path=manifest)
    (tmp_path / "photo.jpg").write_bytes(b"new")

    with pytest.raises(FileExistsError, match="Destination already exists"):
        undo_renames(manifest)

    assert (tmp_path / "image_1.jpg").read_bytes() == b"original"
    assert (tmp_path / "photo.jpg").read_bytes() == b"new"


def test_existing_manifest_blocks_rename_before_files_change(tmp_path):
    image = tmp_path / "photo.jpg"
    image.write_bytes(b"photo")
    manifest = tmp_path / "manifest.json"
    manifest.write_text("existing", encoding="utf-8")

    with pytest.raises(FileExistsError, match="Manifest already exists"):
        rename_images(tmp_path, manifest_path=manifest)

    assert image.read_bytes() == b"photo"


def test_manifest_rejects_path_traversal(tmp_path):
    manifest = tmp_path / "unsafe.json"
    manifest.write_text(
        json.dumps(
            {
                "version": 1,
                "status": "applied",
                "directory": str(tmp_path.resolve()),
                "operations": [{"source": "../outside.jpg", "destination": "image_1.jpg"}],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match="source filename"):
        undo_renames(manifest, dry_run=True)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ({"version": 2}, "version"),
        ({"version": 1, "status": "failed"}, "status"),
        (
            {"version": 1, "status": "applied", "directory": "relative", "operations": []},
            "absolute path",
        ),
        (
            {
                "version": 1,
                "status": "applied",
                "directory": None,
                "operations": [],
            },
            "absolute path",
        ),
    ],
)
def test_manifest_rejects_invalid_metadata(tmp_path, payload, message):
    manifest = tmp_path / "invalid.json"
    manifest.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ManifestError, match=message):
        undo_renames(manifest, dry_run=True)


def test_manifest_rejects_invalid_json(tmp_path):
    manifest = tmp_path / "invalid.json"
    manifest.write_text("not json", encoding="utf-8")

    with pytest.raises(ManifestError, match="not valid JSON"):
        undo_renames(manifest, dry_run=True)


def test_manifest_requires_operations(tmp_path):
    manifest = tmp_path / "empty.json"
    manifest.write_text(
        json.dumps(
            {
                "version": 1,
                "status": "applied",
                "directory": str(tmp_path.resolve()),
                "operations": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ManifestError, match="at least one operation"):
        undo_renames(manifest, dry_run=True)


def test_undone_manifest_cannot_be_reused(tmp_path):
    (tmp_path / "photo.jpg").write_bytes(b"photo")
    manifest = tmp_path / "manifest.json"
    rename_images(tmp_path, manifest_path=manifest)
    undo_renames(manifest)

    with pytest.raises(ManifestError, match="cannot be undone"):
        undo_renames(manifest)


def test_rename_images_rejects_missing_folder(tmp_path):
    with pytest.raises(FileNotFoundError, match="Folder not found"):
        rename_images(tmp_path / "missing")


def test_rename_images_rejects_file(tmp_path):
    file_path = tmp_path / "image.jpg"
    file_path.write_bytes(b"image")
    with pytest.raises(NotADirectoryError, match="Not a directory"):
        rename_images(file_path)
