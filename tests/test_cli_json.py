import json
import subprocess
import sys


def run_cli(*arguments):
    return subprocess.run(
        [sys.executable, "-m", "creator_toolkit.main", *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def test_installed_cli_emits_valid_title_json():
    result = run_cli("title", "creator workflow", "--json")

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["command"] == "title"
    assert payload["ok"] is True
    assert "Creator Workflow" in payload["result"]["title"]


def test_installed_cli_emits_json_error_to_stderr(tmp_path):
    result = run_cli("rename", str(tmp_path / "missing"), "--dry-run", "--json")

    assert result.returncode == 1
    assert result.stdout == ""
    payload = json.loads(result.stderr)
    assert payload["command"] == "rename"
    assert payload["ok"] is False
    assert payload["error"]["type"] == "FileNotFoundError"


def test_installed_cli_rename_preview_is_non_mutating(tmp_path):
    image = tmp_path / "photo.jpg"
    image.write_bytes(b"photo")

    result = run_cli("rename", str(tmp_path), "--dry-run", "--json")

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["status"] == "preview"
    assert image.exists()
