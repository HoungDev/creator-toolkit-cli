# Changelog

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Scriptable `title`, `tags`, and `rename` subcommands.
- Safe rename previews, confirmation, recovery manifests, and an `undo` command.
- Machine-readable JSON output for every scriptable subcommand.
- Installed CLI smoke coverage on Windows, macOS, and Linux.
- Python 3.11–3.13 test matrix, linting, coverage, and distribution checks.

### Changed

- Image renaming is deterministic and avoids collisions with existing numbered files.
- Packaging metadata and contributor documentation are more complete.
