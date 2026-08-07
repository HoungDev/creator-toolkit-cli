# Creator Toolkit CLI

[![Python CI](https://github.com/HoungDev/creator-toolkit-cli/actions/workflows/python-ci.yml/badge.svg)](https://github.com/HoungDev/creator-toolkit-cli/actions/workflows/python-ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-3776AB.svg)](https://www.python.org/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight Python CLI for repeatable creator workflows. Generate content ideas and tags,
or normalize a folder of image names from an interactive menu or scriptable subcommands.

## Features

- Generate title ideas from a keyword.
- Select unique tags from a curated list.
- Rename JPEG and PNG files deterministically without filename collisions.
- Use automation-friendly subcommands or an interactive menu.

## Requirements

- Python 3.11+

## Installation

Install from source in an isolated environment:

```bash
git clone https://github.com/HoungDev/creator-toolkit-cli.git
cd creator-toolkit-cli
python -m pip install .
```

## Usage

Generate a title or tags:

```bash
creator-toolkit title "video editing"
creator-toolkit tags --count 5
```

Rename `.jpg`, `.jpeg`, and `.png` files in a directory:

```bash
creator-toolkit rename ./images
```

The rename command orders inputs by filename and safely produces names such as `image_1.jpg`.
Other files are left untouched. Commit or back up valuable assets before any bulk rename.

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

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full contribution workflow. Bug reports and
focused pull requests are welcome.

## License

[MIT](LICENSE) © 2026 HoungDev contributors.
