from creator_toolkit.main import interactive_menu, main


def test_title_command(capsys):
    assert main(["title", "python"]) == 0
    assert "Python" in capsys.readouterr().out


def test_tags_command(capsys):
    assert main(["tags", "--count", "2"]) == 0
    assert len(capsys.readouterr().out.splitlines()) == 2


def test_rename_command_reports_missing_folder(tmp_path, capsys):
    assert main(["rename", str(tmp_path / "missing"), "--dry-run"]) == 1
    assert "Folder not found" in capsys.readouterr().out


def test_rename_command_dry_run_changes_nothing(tmp_path, capsys):
    image = tmp_path / "photo.jpg"
    image.write_bytes(b"photo")

    assert main(["rename", str(tmp_path), "--dry-run"]) == 0

    output = capsys.readouterr().out
    assert "Planned 1 image(s)." in output
    assert image.exists()
    assert not list(tmp_path.glob(".creator-toolkit-renames-*.json"))


def test_rename_command_cancelled_by_default(tmp_path, monkeypatch, capsys):
    image = tmp_path / "photo.jpg"
    image.write_bytes(b"photo")
    monkeypatch.setattr("builtins.input", lambda _prompt: "n")

    assert main(["rename", str(tmp_path)]) == 0

    assert "Cancelled; no files were changed." in capsys.readouterr().out
    assert image.exists()


def test_rename_command_cancels_on_end_of_input(tmp_path, monkeypatch, capsys):
    image = tmp_path / "photo.jpg"
    image.write_bytes(b"photo")

    def end_of_input(_prompt):
        raise EOFError

    monkeypatch.setattr("builtins.input", end_of_input)

    assert main(["rename", str(tmp_path)]) == 0
    assert "Cancelled; no files were changed." in capsys.readouterr().out
    assert image.exists()


def test_rename_and_undo_commands(tmp_path, capsys):
    (tmp_path / "photo.jpg").write_bytes(b"photo")

    assert main(["rename", str(tmp_path), "--yes"]) == 0
    rename_output = capsys.readouterr().out
    manifest = next(tmp_path.glob(".creator-toolkit-renames-*.json"))
    assert "Renamed 1 image(s)." in rename_output
    assert "Undo manifest:" in rename_output
    assert (tmp_path / "image_1.jpg").exists()

    assert main(["undo", str(manifest), "--dry-run"]) == 0
    assert "Planned restore of 1 image(s)." in capsys.readouterr().out
    assert (tmp_path / "image_1.jpg").exists()

    assert main(["undo", str(manifest), "--yes"]) == 0
    assert "Restored 1 image(s)." in capsys.readouterr().out
    assert (tmp_path / "photo.jpg").read_bytes() == b"photo"


def test_undo_command_cancelled(tmp_path, monkeypatch, capsys):
    (tmp_path / "photo.jpg").write_bytes(b"photo")
    manifest = tmp_path / "manifest.json"
    assert main(["rename", str(tmp_path), "--yes", "--manifest", str(manifest)]) == 0
    capsys.readouterr()
    monkeypatch.setattr("builtins.input", lambda _prompt: "")

    assert main(["undo", str(manifest)]) == 0

    assert "Cancelled; no files were changed." in capsys.readouterr().out
    assert (tmp_path / "image_1.jpg").exists()


def test_undo_command_reports_invalid_manifest(tmp_path, capsys):
    manifest = tmp_path / "invalid.json"
    manifest.write_text("not json", encoding="utf-8")

    assert main(["undo", str(manifest), "--yes"]) == 1
    assert "not valid JSON" in capsys.readouterr().out


def test_interactive_title(monkeypatch, capsys):
    answers = iter(["1", "python"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    assert interactive_menu() == 0
    assert "Python" in capsys.readouterr().out


def test_interactive_tags(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _prompt: "2")
    monkeypatch.setattr("creator_toolkit.main.generate_tags", lambda: ["tag-one", "tag-two"])

    assert interactive_menu() == 0
    assert "['tag-one', 'tag-two']" in capsys.readouterr().out


def test_interactive_rename_success(tmp_path, monkeypatch, capsys):
    (tmp_path / "photo.png").write_bytes(b"photo")
    answers = iter(["3", str(tmp_path), "yes"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    assert interactive_menu() == 0
    assert "Renamed 1 image(s)." in capsys.readouterr().out


def test_interactive_rename_error(tmp_path, monkeypatch, capsys):
    answers = iter(["3", str(tmp_path / "missing")])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    assert interactive_menu() == 1
    assert "Folder not found" in capsys.readouterr().out


def test_interactive_invalid_option(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _prompt: "invalid")

    assert interactive_menu() == 1
    assert "Invalid option" in capsys.readouterr().out
