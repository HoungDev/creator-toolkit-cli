# Contributing

Thank you for considering a contribution to Creator Toolkit CLI.

1. Fork the repository and create a focused branch.
2. Create a virtual environment and install the development tools:

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
```

3. Make your changes and add tests for new behavior.
4. Run the same quality checks used in CI:

```bash
ruff check .
ruff format --check .
pytest
python -m build
python -m twine check dist/*
```

5. Commit and push your branch, then open a pull request.

Please keep changes clear, focused, and well tested. By participating, you agree to follow
the [Code of Conduct](CODE_OF_CONDUCT.md).
