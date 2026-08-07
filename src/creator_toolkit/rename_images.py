from pathlib import Path
from uuid import uuid4

SUPPORTED_EXTENSIONS = {".jpeg", ".jpg", ".png"}


def rename_images(folder: str | Path) -> list[tuple[Path, Path]]:
    """Rename supported images deterministically and return old/new path pairs.

    A two-phase rename prevents existing names such as ``image_1.jpg`` from
    overwriting another input file.
    """
    path = Path(folder)
    if not path.exists():
        raise FileNotFoundError(f"Folder not found: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")

    images = sorted(
        (
            item
            for item in path.iterdir()
            if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=lambda item: item.name.casefold(),
    )
    planned = [
        path / f"image_{index}{image.suffix.lower()}" for index, image in enumerate(images, start=1)
    ]
    staged: list[tuple[Path, Path, Path]] = []

    for source, destination in zip(images, planned, strict=True):
        temporary = path / f".creator-toolkit-{uuid4().hex}.tmp"
        source.rename(temporary)
        staged.append((source, temporary, destination))

    results: list[tuple[Path, Path]] = []
    for source, temporary, destination in staged:
        temporary.rename(destination)
        results.append((source, destination))

    return results
