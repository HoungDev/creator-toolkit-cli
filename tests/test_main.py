from creator_toolkit.main import interactive_menu, main


def test_title_command(capsys):
    assert main(["title", "python"]) == 0
    assert "Python" in capsys.readouterr().out


def test_tags_command(capsys):
    assert main(["tags", "--count", "2"]) == 0
    assert len(capsys.readouterr().out.splitlines()) == 2


def test_rename_command_reports_missing_folder(tmp_path, capsys):
    assert main(["rename", str(tmp_path / "missing")]) == 1
    assert "Folder not found" in capsys.readouterr().out


def test_rename_command_success(tmp_path, capsys):
    (tmp_path / "photo.jpg").write_bytes(b"photo")

    assert main(["rename", str(tmp_path)]) == 0
    assert "photo.jpg -> image_1.jpg" in capsys.readouterr().out


def test_interactive_title(monkeypatch, capsys):
    answers = iter(["1", "python"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(answers))

    assert interactive_menu() == 0
    assert "Python" in capsys.readouterr().out


def test_interactive_tags(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda _prompt: "2")

    assert interactive_menu() == 0
    output = capsys.readouterr().out
    assert "python" in output or "automation" in output


def test_interactive_rename_success(tmp_path, monkeypatch, capsys):
    (tmp_path / "photo.png").write_bytes(b"photo")
    answers = iter(["3", str(tmp_path)])
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
