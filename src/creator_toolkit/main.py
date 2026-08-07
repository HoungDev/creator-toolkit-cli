import argparse
from collections.abc import Sequence
from pathlib import Path

from creator_toolkit.rename_images import (
    ManifestError,
    RenameOperation,
    generate_manifest_path,
    plan_image_renames,
    rename_images,
    undo_renames,
)
from creator_toolkit.tag_generator import generate_tags
from creator_toolkit.title_generator import generate_title


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="creator-toolkit", description="Tools for creator workflows"
    )
    subparsers = parser.add_subparsers(dest="command")
    title_parser = subparsers.add_parser("title", help="generate a title from a keyword")
    title_parser.add_argument("keyword")
    tags_parser = subparsers.add_parser("tags", help="generate a set of tags")
    tags_parser.add_argument("--count", type=int, default=5)

    rename_parser = subparsers.add_parser("rename", help="safely rename images in a directory")
    rename_parser.add_argument("folder")
    rename_parser.add_argument("--dry-run", action="store_true", help="preview without renaming")
    rename_parser.add_argument("--yes", action="store_true", help="apply without confirmation")
    rename_parser.add_argument("--manifest", type=Path, help="custom recovery manifest path")

    undo_parser = subparsers.add_parser("undo", help="reverse an applied rename manifest")
    undo_parser.add_argument("manifest", type=Path)
    undo_parser.add_argument("--dry-run", action="store_true", help="preview without restoring")
    undo_parser.add_argument("--yes", action="store_true", help="restore without confirmation")
    return parser


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
) -> int:
    """Preview and optionally apply an image rename plan."""
    try:
        operations = plan_image_renames(folder)
        print_operations("Planned", operations)
        if dry_run or not operations:
            return 0
        if not assume_yes and not _confirmed("Apply these changes? [y/N]: "):
            print("Cancelled; no files were changed.")
            return 0

        manifest = (
            Path(manifest_path) if manifest_path is not None else generate_manifest_path(folder)
        )
        applied = rename_images(folder, manifest_path=manifest)
        print_operations("Renamed", applied)
        print(f"Undo manifest: {manifest}")
        return 0
    except (
        FileNotFoundError,
        NotADirectoryError,
        FileExistsError,
        ManifestError,
        OSError,
        RuntimeError,
    ) as error:
        print(error)
        return 1


def run_undo(manifest: str | Path, *, dry_run: bool, assume_yes: bool) -> int:
    """Preview and optionally reverse a rename manifest."""
    try:
        operations = undo_renames(manifest, dry_run=True)
        print_operations("Planned restore of", operations)
        if dry_run:
            return 0
        if not assume_yes and not _confirmed("Restore these filenames? [y/N]: "):
            print("Cancelled; no files were changed.")
            return 0
        restored = undo_renames(manifest)
        print_operations("Restored", restored)
        return 0
    except (
        FileNotFoundError,
        NotADirectoryError,
        FileExistsError,
        ManifestError,
        OSError,
        RuntimeError,
    ) as error:
        print(error)
        return 1


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
            input("Enter folder path: "), dry_run=False, assume_yes=False, manifest_path=None
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
        print(generate_title(args.keyword))
    elif args.command == "tags":
        print("\n".join(generate_tags(args.count)))
    elif args.command == "rename":
        return run_rename(
            args.folder,
            dry_run=args.dry_run,
            assume_yes=args.yes,
            manifest_path=args.manifest,
        )
    elif args.command == "undo":
        return run_undo(args.manifest, dry_run=args.dry_run, assume_yes=args.yes)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
