import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

SUPPORTED_EXTENSIONS = {".jpeg", ".jpg", ".png"}
MANIFEST_VERSION = 1
DEFAULT_RENAME_PREFIX = "image"
MAX_FILENAME_COMPONENT_LENGTH = 255

_WINDOWS_INVALID_CHARACTERS = frozenset('<>:"/\\|?*')
_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
    "COM¹",
    "COM²",
    "COM³",
    "LPT¹",
    "LPT²",
    "LPT³",
}

RenameOperation = tuple[Path, Path]


class ManifestError(ValueError):
    """Raised when a rename manifest is invalid or unsafe."""


class InvalidPrefixError(ValueError):
    """Raised when a rename prefix is unsafe as a filename component."""


def _component_lengths(value: str) -> tuple[int, int]:
    try:
        return len(value.encode("utf-8")), len(value.encode("utf-16-le")) // 2
    except UnicodeEncodeError as error:
        raise InvalidPrefixError("Prefix contains unsupported Unicode characters.") from error


def _validate_component_length(value: str, *, generated: bool = False) -> None:
    utf8_length, utf16_length = _component_lengths(value)
    if max(utf8_length, utf16_length) <= MAX_FILENAME_COMPONENT_LENGTH:
        return

    subject = "Generated filename" if generated else "Prefix"
    raise InvalidPrefixError(
        f"{subject} exceeds the cross-platform filename limit of "
        f"{MAX_FILENAME_COMPONENT_LENGTH} characters or bytes."
    )


def validate_rename_prefix(prefix: str) -> str:
    """Return ``prefix`` when it is safe on Windows, macOS, and Linux."""
    if not isinstance(prefix, str) or not prefix or not prefix.strip():
        raise InvalidPrefixError("Prefix must not be empty.")
    if prefix != prefix.strip():
        raise InvalidPrefixError("Prefix must not start or end with whitespace.")
    if prefix in {".", ".."}:
        raise InvalidPrefixError("Prefix must be a single filename component.")
    if prefix.endswith("."):
        raise InvalidPrefixError("Prefix must not end with a period.")
    if any(character in _WINDOWS_INVALID_CHARACTERS or ord(character) < 32 for character in prefix):
        raise InvalidPrefixError("Prefix contains characters that are unsafe in filenames.")

    windows_stem = prefix.split(".", maxsplit=1)[0].upper()
    if windows_stem in _WINDOWS_RESERVED_NAMES:
        raise InvalidPrefixError("Prefix is a reserved filename on Windows.")

    _validate_component_length(prefix)
    return prefix


def _validate_directory(folder: str | Path) -> Path:
    path = Path(folder)
    if not path.exists():
        raise FileNotFoundError(f"Folder not found: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"Not a directory: {path}")
    return path


def plan_image_renames(
    folder: str | Path, *, prefix: str = DEFAULT_RENAME_PREFIX
) -> list[RenameOperation]:
    """Return deterministic image rename operations without changing files."""
    prefix = validate_rename_prefix(prefix)
    path = _validate_directory(folder)
    images = sorted(
        (
            item
            for item in path.iterdir()
            if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        key=lambda item: item.name.casefold(),
    )
    operations: list[RenameOperation] = []
    for index, image in enumerate(images, start=1):
        destination_name = f"{prefix}_{index}{image.suffix.lower()}"
        _validate_component_length(destination_name, generated=True)
        operations.append((image, path / destination_name))
    return [(source, destination) for source, destination in operations if source != destination]


def _validate_operations(operations: list[RenameOperation]) -> None:
    sources = {source for source, _ in operations}
    destinations = [destination for _, destination in operations]
    if len(sources) != len(operations) or len(set(destinations)) != len(operations):
        raise ValueError("Rename plan contains duplicate paths.")

    for source, destination in operations:
        if not source.is_file():
            raise FileNotFoundError(f"Source file not found: {source}")
        if source.parent != destination.parent:
            raise ValueError("Rename operations must stay in the same directory.")
        if destination.exists() and destination not in sources:
            raise FileExistsError(f"Destination already exists: {destination}")


def _temporary_path(path: Path, label: str) -> Path:
    return path.parent / f".creator-toolkit-{label}-{uuid4().hex}.tmp"


def _restore_staged(staged: list[tuple[Path, Path, Path]]) -> None:
    for source, temporary, _ in reversed(staged):
        if temporary.exists():
            temporary.rename(source)


def _restore_after_finalize_failure(
    staged: list[tuple[Path, Path, Path]], finalized_count: int
) -> None:
    rollback_staged: list[tuple[Path, Path]] = []
    for index, (source, temporary, destination) in enumerate(staged):
        current = destination if index < finalized_count else temporary
        rollback_temporary = _temporary_path(source, "rollback")
        current.rename(rollback_temporary)
        rollback_staged.append((source, rollback_temporary))

    for source, rollback_temporary in rollback_staged:
        rollback_temporary.rename(source)


def _apply_operations(operations: list[RenameOperation]) -> None:
    if not operations:
        return
    _validate_operations(operations)
    staged: list[tuple[Path, Path, Path]] = []

    try:
        for source, destination in operations:
            temporary = _temporary_path(source, "stage")
            source.rename(temporary)
            staged.append((source, temporary, destination))
    except OSError as error:
        try:
            _restore_staged(staged)
        except OSError as rollback_error:
            raise RuntimeError(
                "Rename failed and the staged files could not be restored."
            ) from rollback_error
        raise error

    finalized_count = 0
    try:
        for _, temporary, destination in staged:
            temporary.rename(destination)
            finalized_count += 1
    except OSError as error:
        try:
            _restore_after_finalize_failure(staged, finalized_count)
        except OSError as rollback_error:
            raise RuntimeError(
                "Rename failed and rollback could not be completed."
            ) from rollback_error
        raise error


def generate_manifest_path(folder: str | Path) -> Path:
    """Return a unique default manifest path inside ``folder``."""
    path = _validate_directory(folder)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return path / f".creator-toolkit-renames-{timestamp}-{uuid4().hex[:8]}.json"


def _write_manifest(path: Path, payload: dict[str, Any], *, replace: bool) -> None:
    if path.exists() and not replace:
        raise FileExistsError(f"Manifest already exists: {path}")
    if not path.parent.is_dir():
        raise FileNotFoundError(f"Manifest directory not found: {path.parent}")

    temporary = _temporary_path(path, "manifest")
    try:
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _new_manifest(folder: Path, operations: list[RenameOperation]) -> dict[str, Any]:
    return {
        "version": MANIFEST_VERSION,
        "status": "pending",
        "created_at": datetime.now(UTC).isoformat(),
        "directory": str(folder.resolve()),
        "operations": [
            {"source": source.name, "destination": destination.name}
            for source, destination in operations
        ],
    }


def rename_images(
    folder: str | Path,
    *,
    dry_run: bool = False,
    manifest_path: str | Path | None = None,
    prefix: str = DEFAULT_RENAME_PREFIX,
) -> list[RenameOperation]:
    """Plan or apply deterministic image renames with optional recovery metadata."""
    path = _validate_directory(folder)
    operations = plan_image_renames(path, prefix=prefix)
    if dry_run or not operations:
        return operations

    manifest = Path(manifest_path) if manifest_path is not None else None
    payload = _new_manifest(path, operations) if manifest is not None else None
    if manifest is not None and payload is not None:
        _write_manifest(manifest, payload, replace=False)

    try:
        _apply_operations(operations)
    except (OSError, RuntimeError):
        if manifest is not None and payload is not None:
            payload["status"] = "failed"
            _write_manifest(manifest, payload, replace=True)
        raise

    if manifest is not None and payload is not None:
        payload["status"] = "applied"
        payload["applied_at"] = datetime.now(UTC).isoformat()
        _write_manifest(manifest, payload, replace=True)
    return operations


def _safe_manifest_name(value: object, field: str) -> str:
    if not isinstance(value, str) or not value or Path(value).name != value or value in {".", ".."}:
        raise ManifestError(f"Invalid manifest {field} filename.")
    return value


def _load_manifest(manifest_path: str | Path) -> tuple[Path, dict[str, Any], list[RenameOperation]]:
    path = Path(manifest_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ManifestError(f"Manifest is not valid JSON: {path}") from error

    if not isinstance(payload, dict) or payload.get("version") != MANIFEST_VERSION:
        raise ManifestError("Unsupported or missing manifest version.")
    if payload.get("status") not in {"applied", "pending"}:
        raise ManifestError(f"Manifest cannot be undone from status: {payload.get('status')}")

    directory_value = payload.get("directory")
    if not isinstance(directory_value, str) or not Path(directory_value).is_absolute():
        raise ManifestError("Manifest directory must be an absolute path.")
    directory = _validate_directory(directory_value)

    raw_operations = payload.get("operations")
    if not isinstance(raw_operations, list) or not raw_operations:
        raise ManifestError("Manifest must contain at least one operation.")

    operations: list[RenameOperation] = []
    for operation in raw_operations:
        if not isinstance(operation, dict):
            raise ManifestError("Manifest operation must be an object.")
        source = _safe_manifest_name(operation.get("source"), "source")
        destination = _safe_manifest_name(operation.get("destination"), "destination")
        operations.append((directory / destination, directory / source))

    _validate_operations(operations)
    return path, payload, operations


def undo_renames(manifest_path: str | Path, *, dry_run: bool = False) -> list[RenameOperation]:
    """Reverse an applied rename manifest, optionally as a preview only."""
    path, payload, operations = _load_manifest(manifest_path)
    if dry_run:
        return operations

    _apply_operations(operations)
    payload["status"] = "undone"
    payload["undone_at"] = datetime.now(UTC).isoformat()
    _write_manifest(path, payload, replace=True)
    return operations
