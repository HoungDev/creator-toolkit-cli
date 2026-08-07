# Changelog

All notable changes to this project are documented in this file. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-08-07

### Added

- Reproducible title and tag generation with an optional local random seed.
- Cross-platform-safe custom prefixes for image rename previews, applies, JSON output, and undo
  manifests.

### Changed

- Installation guidance now prefers the published PyPI package and links to verified release
  artifacts.
- Contributor onboarding and the pull request template now provide clearer scope, validation, and
  review expectations.
- The animated README demo is shorter, uses real CLI output, and reproduces suggestion examples
  with a fixed seed.

## [0.1.0] - 2026-08-07

### Added

- Scriptable `title`, `tags`, and `rename` subcommands.
- Safe rename previews, confirmation, recovery manifests, and an `undo` command.
- Machine-readable JSON output for every scriptable subcommand.
- Installed CLI smoke coverage on Windows, macOS, and Linux.
- Reproducible animated README demo with real title, tag, and rename-preview workflows.
- Manually approved Trusted Publishing workflow and release checklist for PyPI and TestPyPI.
- Python 3.11–3.13 test matrix, linting, coverage, and distribution checks.

### Changed

- Image renaming is deterministic and avoids collisions with existing numbered files.
- Packaging metadata and contributor documentation are more complete.

[Unreleased]: https://github.com/HoungDev/creator-toolkit-cli/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/HoungDev/creator-toolkit-cli/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/HoungDev/creator-toolkit-cli/releases/tag/v0.1.0
