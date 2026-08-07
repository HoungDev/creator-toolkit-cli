"""Render the animated README demo from real Creator Toolkit CLI output."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
DEFAULT_OUTPUT = ROOT / "docs" / "assets" / "creator-toolkit-demo.gif"
WIDTH = 900
HEIGHT = 506
SEED = 2026

BACKGROUND = "#0d1117"
PANEL = "#161b22"
BORDER = "#30363d"
TEXT = "#e6edf3"
MUTED = "#8b949e"
GREEN = "#3fb950"
BLUE = "#58a6ff"
PURPLE = "#a371f7"

Line = tuple[str, str]


def _font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a readable system monospace font on the supported platforms."""
    filename = "consolab.ttf" if bold else "consola.ttf"
    candidates = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / filename,
        Path(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
            if bold
            else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        ),
        Path("/System/Library/Fonts/Menlo.ttc"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default(size=size)


def _run_cli(arguments: list[str], *, cwd: Path) -> list[str]:
    """Run the current source tree and return its output lines."""
    environment = os.environ.copy()
    current_pythonpath = environment.get("PYTHONPATH")
    environment["PYTHONPATH"] = os.pathsep.join(
        value for value in (str(SOURCE), current_pythonpath) if value
    )
    runner = (
        "import sys; from creator_toolkit.main import main; raise SystemExit(main(sys.argv[1:]))"
    )
    result = subprocess.run(
        [sys.executable, "-c", runner, *arguments],
        cwd=cwd,
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip().splitlines()


def _capture_scenes() -> list[tuple[str, list[Line]]]:
    """Capture title, tag, and safe-rename scenes from non-sensitive sample data."""
    with tempfile.TemporaryDirectory(prefix="creator-toolkit-demo-") as temporary_directory:
        workspace = Path(temporary_directory)
        images = workspace / "demo-images"
        images.mkdir()
        (images / "cover.jpg").write_bytes(b"demo")
        (images / "thumbnail.png").write_bytes(b"demo")

        title = _run_cli(["title", "creator workflow", "--seed", str(SEED)], cwd=workspace)
        tags = _run_cli(["tags", "--count", "3", "--seed", str(SEED)], cwd=workspace)
        rename = _run_cli(
            ["rename", "demo-images", "--prefix", "campaign", "--dry-run"], cwd=workspace
        )

    return [
        (
            "TITLE IDEAS",
            [
                ("prompt", '$ creator-toolkit title "creator workflow" --seed 2026'),
                *(("output", line) for line in title),
                ("blank", ""),
                ("note", "Turn one keyword into a ready-to-refine headline."),
            ],
        ),
        (
            "CURATED TAGS",
            [
                ("prompt", "$ creator-toolkit tags --count 3 --seed 2026"),
                *(("output", line) for line in tags),
                ("blank", ""),
                ("note", "Unique suggestions, sorted for predictable output."),
            ],
        ),
        (
            "SAFE RENAME PREVIEW",
            [
                ("muted", "demo-images/"),
                ("muted", "  cover.jpg"),
                ("muted", "  thumbnail.png"),
                ("blank", ""),
                ("prompt", "$ creator-toolkit rename demo-images --prefix campaign --dry-run"),
                *(("output", line) for line in rename),
                ("blank", ""),
                ("success", "Preview only - no files changed."),
            ],
        ),
    ]


def _draw_frame(label: str, lines: list[Line], step: int, total: int) -> Image.Image:
    """Draw one terminal-style frame."""
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    body_font = _font(22)
    body_bold = _font(22, bold=True)
    small_font = _font(16)

    draw.rounded_rectangle((18, 18, WIDTH - 18, HEIGHT - 18), radius=14, fill=PANEL, outline=BORDER)
    for x, color in ((42, "#ff5f56"), (66, "#ffbd2e"), (90, "#27c93f")):
        draw.ellipse((x - 6, 38, x + 6, 50), fill=color)
    draw.text((WIDTH // 2, 44), "creator-toolkit - demo", font=small_font, fill=MUTED, anchor="mm")
    draw.line((19, 68, WIDTH - 19, 68), fill=BORDER, width=1)

    draw.rounded_rectangle((42, 86, 42 + 20 + len(label) * 10, 118), radius=16, fill="#21262d")
    draw.text((54, 102), label, font=small_font, fill=PURPLE, anchor="lm")

    colors = {
        "prompt": GREEN,
        "output": TEXT,
        "muted": MUTED,
        "note": BLUE,
        "success": GREEN,
        "blank": TEXT,
    }
    y = 142
    for kind, line in lines:
        font = body_bold if kind in {"prompt", "success"} else body_font
        prefix = "[ok] " if kind == "success" else ""
        draw.text((48, y), prefix + line, font=font, fill=colors[kind])
        y += 31

    footer = "safe previews  |  JSON output  |  undo manifests"
    draw.text((44, HEIGHT - 41), footer, font=small_font, fill=MUTED, anchor="lm")
    draw.text(
        (WIDTH - 44, HEIGHT - 41), f"{step}/{total}", font=small_font, fill=MUTED, anchor="rm"
    )
    return image


def render(output: Path) -> None:
    """Capture CLI output and write the optimized looping GIF."""
    scenes = _capture_scenes()
    frames = [
        _draw_frame(label, lines, step=index, total=len(scenes))
        for index, (label, lines) in enumerate(scenes, start=1)
    ]
    palette_frames = [
        frame.quantize(colors=64, method=Image.Quantize.MEDIANCUT) for frame in frames
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    palette_frames[0].save(
        output,
        save_all=True,
        append_images=palette_frames[1:],
        duration=[2200, 2200, 3200],
        loop=0,
        optimize=True,
        disposal=2,
    )


def main() -> None:
    """Parse arguments and render the README demo."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    render(arguments.output.resolve())
    print(f"Rendered {arguments.output.resolve()}")


if __name__ == "__main__":
    main()
