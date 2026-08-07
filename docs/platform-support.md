# Platform support

Creator Toolkit CLI supports Python 3.11–3.13 on current Windows, macOS, and Linux systems.

## Continuous integration policy

The CI suite uses two complementary matrices:

- Unit, coverage, lint, audit, and distribution checks run on Ubuntu across Python 3.11, 3.12,
  and 3.13.
- Installed CLI smoke tests run on the current GitHub-hosted Ubuntu, macOS, and Windows images
  with Python 3.12.

The cross-platform jobs install the package with `pip install .` and invoke the generated
`creator-toolkit` console entrypoint. They cover command help, title generation, tag generation,
non-mutating image rename previews, structured diagnostics, and failure exit codes.

## Support expectations

- Bugs reproduced on the tested matrix are treated as supported-platform defects.
- Other Python 3 implementations, end-of-life Python releases, and older operating system
  versions may work but are not continuously verified.
- Filesystem behavior can differ by platform. Rename safety and rollback tests therefore run in
  both the unit suite and installed CLI smoke suite.

When reporting a platform-specific issue, include the operating system, Python version, install
method, command, exit code, and complete stdout/stderr output. Do not include sensitive paths or
file contents.
