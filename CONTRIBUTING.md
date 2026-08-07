# Contributing

Thank you for helping make Creator Toolkit CLI safer and more useful for creator workflows.
Focused bug fixes, documentation improvements, tests, and small features are welcome.

## Find work and signal your intent

- Start with an open
  [`good first issue`](https://github.com/HoungDev/creator-toolkit-cli/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22good%20first%20issue%22)
  or [`help wanted`](https://github.com/HoungDev/creator-toolkit-cli/issues?q=is%3Aissue%20state%3Aopen%20label%3A%22help%20wanted%22)
  issue.
- Comment with the approach you plan to take before investing significant time. This helps avoid
  duplicate work and gives maintainers a chance to clarify edge cases.
- Keep the pull request focused on one issue. Propose larger or unrelated behavior separately
  through the [issue chooser](https://github.com/HoungDev/creator-toolkit-cli/issues/new/choose).
- Report vulnerabilities through
  [private vulnerability reporting](https://github.com/HoungDev/creator-toolkit-cli/security/advisories/new),
  not a public issue.

## Set up the project

Fork the repository, clone your fork, and create a descriptive branch:

```bash
git clone https://github.com/YOUR-USERNAME/creator-toolkit-cli.git
cd creator-toolkit-cli
git switch -c fix/short-description
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install the project and development tools, then verify the CLI is available:

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
creator-toolkit --help
```

Install `.[dev,demo]` instead when changing the generated README demo.

## Make a focused change

- Add or update tests for behavior changes and regressions.
- Preserve documented CLI, JSON, manifest, and exit-code compatibility unless the issue explicitly
  calls for a breaking change.
- Update user-facing documentation when flags, output, or workflows change.
- Do not commit credentials, tokens, local environments, build output, or real user files.

Run focused tests while developing, then run the full local quality suite:

```bash
ruff check .
ruff format --check .
pytest
python -m build
python -m twine check dist/*
```

If the README demo changes, rebuild its tracked asset from real CLI output:

```bash
python scripts/render_readme_demo.py
```

CI repeats the quality suite on Python 3.11–3.13 and smoke-tests the installed command on Windows,
macOS, and Ubuntu.

## Open a pull request

Push your branch and open a pull request against `main`. Draft pull requests are welcome when you
want early feedback. Complete the repository template with:

- the linked issue, using `Closes #123` when the PR fully resolves it;
- a concise explanation of what changed and why;
- compatibility or safety impact, including `None` when not applicable;
- the exact commands used to validate the change.

Keep review follow-ups in the same focused branch and avoid unrelated formatting or refactoring.
Maintainers may ask for smaller scope, additional edge-case tests, or documentation before merge.

Please keep changes clear, focused, and well tested. By participating, you agree to follow
the [Code of Conduct](CODE_OF_CONDUCT.md).
