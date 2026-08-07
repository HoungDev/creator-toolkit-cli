import json
import shutil
import subprocess
import sys
from pathlib import Path


def installed_cli() -> str:
    executable = shutil.which("creator-toolkit")
    if executable is not None:
        return executable

    script_name = "creator-toolkit.exe" if sys.platform == "win32" else "creator-toolkit"
    candidate = Path(sys.executable).with_name(script_name)
    assert candidate.is_file(), f"Installed CLI not found at {candidate}"
    return str(candidate)


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [installed_cli(), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )


def assert_success(result: subprocess.CompletedProcess[str]) -> None:
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"


def test_installed_cli_help_lists_commands():
    result = run_cli("--help")

    assert_success(result)
    assert result.stderr == ""
    for command in ("title", "tags", "rename", "undo"):
        assert command in result.stdout


def test_installed_cli_generates_title_and_tags_json():
    title_result = run_cli("title", "creator workflow", "--seed", "2026", "--json")
    assert_success(title_result)
    title = json.loads(title_result.stdout)
    assert title["command"] == "title"
    assert "Creator Workflow" in title["result"]["title"]
    assert run_cli("title", "creator workflow", "--seed", "2026", "--json").stdout == (
        title_result.stdout
    )

    tags_result = run_cli("tags", "--count", "3", "--seed", "2026", "--json")
    assert_success(tags_result)
    tags = json.loads(tags_result.stdout)
    assert tags["command"] == "tags"
    assert tags["result"]["count"] == 3
    assert run_cli("tags", "--count", "3", "--seed", "2026", "--json").stdout == (
        tags_result.stdout
    )


def test_installed_cli_rename_preview_does_not_change_files(tmp_path):
    image = tmp_path / "photo.jpg"
    image.write_bytes(b"photo")

    result = run_cli("rename", str(tmp_path), "--prefix", "campaign", "--dry-run", "--json")

    assert_success(result)
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["status"] == "preview"
    assert payload["result"]["operations"] == [
        {"source": "photo.jpg", "destination": "campaign_1.jpg"}
    ]
    assert image.read_bytes() == b"photo"
    assert not (tmp_path / "campaign_1.jpg").exists()


def test_installed_cli_failure_preserves_exit_code_and_diagnostics(tmp_path):
    result = run_cli("rename", str(tmp_path / "missing"), "--dry-run", "--json")

    assert result.returncode == 1
    assert result.stdout == ""
    payload = json.loads(result.stderr)
    assert payload["ok"] is False
    assert payload["error"]["type"] == "FileNotFoundError"
