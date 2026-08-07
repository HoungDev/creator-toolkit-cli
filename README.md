# Creator Toolkit CLI

[![Python CI](https://github.com/HoungDev/creator-toolkit-cli/actions/workflows/python-ci.yml/badge.svg)](https://github.com/HoungDev/creator-toolkit-cli/actions/workflows/python-ci.yml)
[![PyPI](https://img.shields.io/pypi/v/creator-toolkit-cli.svg)](https://pypi.org/project/creator-toolkit-cli/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/HoungDev/creator-toolkit-cli/blob/main/LICENSE)

A lightweight Python CLI for repeatable creator workflows. Generate content ideas and tags,
or normalize a folder of image names from an interactive menu or scriptable subcommands.

![Animated terminal demo showing title generation, tag selection, and a dry-run image rename preview](https://raw.githubusercontent.com/HoungDev/creator-toolkit-cli/main/docs/assets/creator-toolkit-demo.gif)

<sub>The demo uses disposable sample files and a fixed seed for reproducible suggestions.</sub>

## Why Creator Toolkit?

- Preview filename changes before touching a directory, then undo applied renames from a manifest.
- Automate every scriptable workflow with stable JSON schemas and meaningful exit codes.
- Get the same CLI behavior on current Windows, macOS, and Linux systems.
- Keep small creator tasks local, inspectable, and easy to compose in scripts.

## Real workflows

| Goal | Before | Example result |
| --- | --- | --- |
| Draft a title | `creator workflow` | `10 Creator Workflow Tips Every Beginner Should Know` |
| Pick three tags | `--count 3` | `automation`, `productivity`, `tutorial` |
| Preview image renames | `--prefix campaign` | `campaign_1.jpg`, `campaign_2.png` — no files changed |

See the [demo transcript and reproduction steps](https://github.com/HoungDev/creator-toolkit-cli/blob/main/docs/demo.md).

## Features

- Generate title ideas from a keyword.
- Select unique tags from a curated list.
- Preview, apply, and undo deterministic JPEG and PNG filename changes with a safe custom prefix.
- Use automation-friendly subcommands or an interactive menu.

## Requirements

- Python 3.11+
- A current Windows, macOS, or Linux system

See the [platform support policy](https://github.com/HoungDev/creator-toolkit-cli/blob/main/docs/platform-support.md)
for the tested OS/Python matrix and support expectations.

## Installation

Install the latest stable release from PyPI:

```bash
python -m pip install creator-toolkit-cli
```

Release notes and verified distribution hashes are available in the
[latest GitHub release](https://github.com/HoungDev/creator-toolkit-cli/releases/latest).

## Usage

Generate a title or tags:

```bash
creator-toolkit title "video editing"
creator-toolkit tags --count 5
```

Pass the same integer seed to reproduce a title or tag set; omit it for fresh suggestions:

```bash
creator-toolkit title "video editing" --seed 2026
creator-toolkit tags --count 5 --seed 2026
```

Add `--json` to any scriptable subcommand for automation-friendly output:

```bash
creator-toolkit title "video editing" --seed 2026 --json
creator-toolkit tags --count 5 --seed 2026 --json
creator-toolkit rename ./images --prefix campaign --dry-run --json
```

See the [JSON output reference](https://github.com/HoungDev/creator-toolkit-cli/blob/main/docs/json-output.md)
for response schemas, exit codes, error handling, and automation examples.

Preview changes to `.jpg`, `.jpeg`, and `.png` files without touching the directory:

```bash
creator-toolkit rename ./images --prefix campaign --dry-run
```

This produces names such as `campaign_1.jpg`. Omit `--prefix` to retain the default `image_1.jpg`
format. Unsafe filename components and cross-platform reserved names are rejected before any file
or manifest changes.

Apply the displayed plan after an interactive confirmation, using the same prefix:

```bash
creator-toolkit rename ./images --prefix campaign
```

For non-interactive automation, pass `--yes`. Every applied CLI rename writes a unique JSON
manifest in the image directory:

```bash
creator-toolkit rename ./images --prefix campaign --yes
creator-toolkit undo ./images/.creator-toolkit-renames-20260807T120000Z-a1b2c3d4.json --dry-run
creator-toolkit undo ./images/.creator-toolkit-renames-20260807T120000Z-a1b2c3d4.json
```

The rename command orders inputs by filename and uses a two-phase rename to avoid collisions and
roll back when a filesystem step fails. Undo manifests store concrete operations, so undo does not
need the original prefix. They reject path traversal and refuse to overwrite files created after
the rename. Other files are left untouched, but a separate backup is still recommended for
valuable assets.

Run without a subcommand to use the interactive menu:

```bash
creator-toolkit
```

## Development

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
```

See [CONTRIBUTING.md](https://github.com/HoungDev/creator-toolkit-cli/blob/main/CONTRIBUTING.md)
for the full contribution workflow. Bug reports and focused pull requests are welcome.

Maintainers should follow the
[release checklist](https://github.com/HoungDev/creator-toolkit-cli/blob/main/docs/releasing.md)
and complete the
[one-time trusted publishing setup](https://github.com/HoungDev/creator-toolkit-cli/blob/main/docs/trusted-publishing.md)
before publishing a version.

## License

[MIT](https://github.com/HoungDev/creator-toolkit-cli/blob/main/LICENSE) © 2026 HoungDev contributors.
