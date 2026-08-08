import argparse
import json
import sys
from collections.abc import Sequence
from importlib import metadata
from pathlib import Path
from random import Random
from typing import Any

from creator_toolkit.rename_images import (
    DEFAULT_RENAME_PREFIX,
    InvalidPrefixError,
    ManifestError,
    RenameOperation,
    generate_manifest_path,
    plan_image_renames,
    rename_images,
    undo_renames,
)
from creator_toolkit.tag_generator import generate_tags
from creator_toolkit.title_generator import generate_title

JSON_SCHEMA_VERSION = 1
PACKAGE_NAME = "creator-toolkit-cli"


class UsageError(ValueError):
    """Raised when a safe non-interactive invocation is incomplete."""


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="creator-toolkit", description="Tools for creator workflows"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{PACKAGE_NAME} {metadata.version(PACKAGE_NAME)}",
        help="show the installed package version and exit",
    )
    subparsers = parser.add_subparsers(dest="command")

    title_parser = subparsers.add_parser("title", help="generate a title from a keyword")
    title_parser.add_argument("keyword")
    title_parser.add_argument("--seed", type=int, help="make generated output reproducible")
    title_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    tags_parser = subparsers.add_parser("tags", help="generate a set of tags")
    tags_parser.add_argument("--count", type=int, default=5)
    tags_parser.add_argument("--seed", type=int, help="make generated output reproducible")
    tags_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    rename_parser = subparsers.add_parser("rename", help="safely rename images in a directory")
    rename_parser.add_argument("folder")
    rename_parser.add_argument("--dry-run", action="store_true", help="preview without renaming")
    rename_parser.add_argument("--yes", action="store_true", help="apply without confirmation")
    rename_parser.add_argument(
        "--prefix",
        default=DEFAULT_RENAME_PREFIX,
        help=f"destination filename prefix (default: {DEFAULT_RENAME_PREFIX})",
    )
    rename_parser.add_argument("--manifest", type=Path, help="custom recovery manifest path")
    rename_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    undo_parser = subparsers.add_parser("undo", help="reverse an applied rename manifest")
    undo_parser.add_argument("manifest", type=Path)
    undo_parser.add_argument("--dry-run", action="store_true", help="preview without restoring")
    undo_parser.add_argument("--yes", action="store_true", help="restore without confirmation")
    undo_parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser


def _operation_records(operations: list[RenameOperation]) -> list[dict[str, str]]:
    return [
        {"source": source.name, "destination": destination.name}
        for source, destination in operations
    ]


def _emit_json(payload: dict[str, Any], *, error: bool = False) -> None:
    stream = sys.stderr if error else sys.stdout
    print(json.dumps(payload, sort_keys=True), file=stream)


def _emit_success(command: str, status: str, result: dict[str, Any]) -> None:
    _emit_json(
        {
            "schema_version": JSON_SCHEMA_VERSION,
            "command": command,
            "ok": True,
            "status": status,
            "result": result,
        }
    )


def _report_error(command: str, error: Exception, *, json_output: bool, exit_code: int) -> int:
    if json_output:
        _emit_json(
            {
                "schema_version": JSON_SCHEMA_VERSION,
                "command": command,
                "ok": False,
                "status": "error",
                "error": {"type": type(error).__name__, "message": str(error)},
            },
            error=True,
        )
    else:
        print(error, file=sys.stderr)
    return exit_code


def print_operations(label: str, operations: list[RenameOperation]) -> None:
    """Print a concise operation summary."""
    print(f"{label} {len(operations)} image(s).")
    for source, destination in operations:
        print(f"{source.name} -> {destination.name}")


def _confirmed(prompt: str) -> bool:
    try:
        return input(prompt).strip().lower() in {"y", "yes"}
    except EOFError:
        return False


def run_rename(
    folder: str | Path,
    *,
    dry_run: bool,
    assume_yes: bool,
    manifest_path: str | Path | None,
    json_output: bool,
    prefix: str = DEFAULT_RENAME_PREFIX,
) -> int:
    """Preview and optionally apply an image rename plan."""
    try:
        if json_output and not (dry_run or assume_yes):
            raise UsageError("JSON rename requires --dry-run or --yes.")

        operations = plan_image_renames(folder, prefix=prefix)
        if not json_output:
            print_operations("Planned", operations)
        if dry_run:
            if json_output:
                _emit_success(
                    "rename",
                    "preview",
                    {
                        "directory": str(Path(folder).resolve()),
                        "manifest": None,
                        "operations": _operation_records(operations),
                    },
                )
            return 0
        if not operations:
            if json_output:
                _emit_success(
                    "rename",
                    "unchanged",
                    {
                        "directory": str(Path(folder).resolve()),
                        "manifest": None,
                        "operations": [],
                    },
                )
            return 0
        if not assume_yes and not _confirmed("Apply these changes? [y/N]: "):
            print("Cancelled; no files were changed.")
            return 0

        manifest = (
            Path(manifest_path) if manifest_path is not None else generate_manifest_path(folder)
        )
        applied = rename_images(folder, manifest_path=manifest, prefix=prefix)
        if json_output:
            _emit_success(
                "rename",
                "applied",
                {
                    "directory": str(Path(folder).resolve()),
                    "manifest": str(manifest.resolve()),
                    "operations": _operation_records(applied),
                },
            )
        else:
            print_operations("Renamed", applied)
            print(f"Undo manifest: {manifest}")
        return 0
    except UsageError as error:
        return _report_error("rename", error, json_output=json_output, exit_code=2)
    except (
        FileNotFoundError,
        NotADirectoryError,
        FileExistsError,
        InvalidPrefixError,
        ManifestError,
        OSError,
        RuntimeError,
    ) as error:
        return _report_error("rename", error, json_output=json_output, exit_code=1)


def run_undo(manifest: str | Path, *, dry_run: bool, assume_yes: bool, json_output: bool) -> int:
    """Preview and optionally reverse a rename manifest."""
    try:
        if json_output and not (dry_run or assume_yes):
            raise UsageError("JSON undo requires --dry-run or --yes.")

        operations = undo_renames(manifest, dry_run=True)
        if not json_output:
            print_operations("Planned restore of", operations)
        if dry_run:
            if json_output:
                _emit_success(
                    "undo",
                    "preview",
                    {
                        "manifest": str(Path(manifest).resolve()),
                        "operations": _operation_records(operations),
                    },
                )
            return 0
        if not assume_yes and not _confirmed("Restore these filenames? [y/N]: "):
            print("Cancelled; no files were changed.")
            return 0

        restored = undo_renames(manifest)
        if json_output:
            _emit_success(
                "undo",
                "restored",
                {
                    "manifest": str(Path(manifest).resolve()),
                    "operations": _operation_records(restored),
                },
            )
        else:
            print_operations("Restored", restored)
        return 0
    except UsageError as error:
        return _report_error("undo", error, json_output=json_output, exit_code=2)
    except (
        FileNotFoundError,
        NotADirectoryError,
        FileExistsError,
        ManifestError,
        OSError,
        RuntimeError,
    ) as error:
        return _report_error("undo", error, json_output=json_output, exit_code=1)


def interactive_menu() -> int:
    """Run the interactive menu."""
    print("Creator Toolkit CLI")
    print("1. Generate title")
    print("2. Generate tags")
    print("3. Rename images")
    choice = input("Choose an option: ")
    if choice == "1":
        print(generate_title(input("Enter keyword: ")))
    elif choice == "2":
        print(generate_tags())
    elif choice == "3":
        return run_rename(
            input("Enter folder path: "),
            dry_run=False,
            assume_yes=False,
            manifest_path=None,
            json_output=False,
            prefix=DEFAULT_RENAME_PREFIX,
        )
    else:
        print("Invalid option")
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit code."""
    args = build_parser().parse_args(argv)
    if args.command is None:
        return interactive_menu()
    if args.command == "title":
        rng = Random(args.seed) if args.seed is not None else None
        title = generate_title(args.keyword, rng=rng)
        if args.json:
            _emit_success("title", "generated", {"title": title})
        else:
            print(title)
    elif args.command == "tags":
        rng = Random(args.seed) if args.seed is not None else None
        tags = generate_tags(args.count, rng=rng)
        if args.json:
            _emit_success("tags", "generated", {"count": len(tags), "tags": tags})
        else:
            print("\n".join(tags))
    elif args.command == "rename":
        return run_rename(
            args.folder,
            dry_run=args.dry_run,
            assume_yes=args.yes,
            manifest_path=args.manifest,
            json_output=args.json,
            prefix=args.prefix,
        )
    elif args.command == "undo":
        return run_undo(
            args.manifest,
            dry_run=args.dry_run,
            assume_yes=args.yes,
            json_output=args.json,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
