import argparse
from collections.abc import Sequence
from pathlib import Path

from creator_toolkit.rename_images import rename_images
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
    rename_parser = subparsers.add_parser("rename", help="rename images in a directory")
    rename_parser.add_argument("folder")
    return parser


def print_renamed(renamed: list[tuple[Path, Path]]) -> None:
    """Print a concise rename summary."""
    print(f"Renamed {len(renamed)} image(s).")
    for source, destination in renamed:
        print(f"{source.name} -> {destination.name}")


def interactive_menu() -> int:
    """Run the original interactive menu."""
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
        folder = input("Enter folder path: ")
        try:
            print_renamed(rename_images(folder))
        except (FileNotFoundError, NotADirectoryError) as error:
            print(error)
            return 1
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
        try:
            print_renamed(rename_images(args.folder))
        except (FileNotFoundError, NotADirectoryError) as error:
            print(error)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
