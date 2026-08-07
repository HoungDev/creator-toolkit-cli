# JSON output

Every scriptable subcommand supports `--json`. Successful responses are written as one JSON
object to standard output. Runtime and validation errors are written as one JSON object to
standard error, leaving standard output empty.

## Envelope

Successful responses use this envelope:

```json
{
  "schema_version": 1,
  "command": "tags",
  "ok": true,
  "status": "generated",
  "result": {
    "count": 2,
    "tags": ["automation", "python"]
  }
}
```

Errors replace `result` with a stable error object:

```json
{
  "schema_version": 1,
  "command": "rename",
  "ok": false,
  "status": "error",
  "error": {
    "type": "FileNotFoundError",
    "message": "Folder not found: ./missing"
  }
}
```

The fields inside `result` depend on the command:

- `title`: `title`.
- `tags`: `count` and `tags`.
- `rename`: `directory`, `manifest`, and `operations`.
- `undo`: `manifest` and `operations`.

Each operation contains `source` and `destination` filenames. Rename statuses are `preview`,
`unchanged`, or `applied`; undo statuses are `preview` or `restored`.

## Reproducible generation

Pass the same integer `--seed` to `title` or `tags` to reproduce the same result for the same
input. The seed changes generated values only: the JSON envelope and schema version remain the
same. Omit `--seed` to keep the normal randomized behavior.

```bash
creator-toolkit title "creator workflow" --seed 2026 --json
creator-toolkit tags --count 3 --seed 2026 --json
```

## Safe non-interactive use

JSON mode never prompts. `rename` and `undo` therefore require either `--dry-run` or `--yes` when
combined with `--json`. Omitting both produces a structured `UsageError` and exit code 2.

## Exit codes

- `0`: success, including previews and human-confirmed cancellation.
- `1`: runtime or validation error.
- `2`: invalid CLI usage or an unsafe JSON-mode invocation.

## Automation examples

Read generated tags from Python:

```python
import json
import subprocess

result = subprocess.run(
    ["creator-toolkit", "tags", "--count", "3", "--seed", "2026", "--json"],
    check=True,
    capture_output=True,
    text=True,
)
tags = json.loads(result.stdout)["result"]["tags"]
print(tags)
```

Inspect a rename plan from PowerShell without modifying files:

```powershell
$plan = creator-toolkit rename .\images --dry-run --json | ConvertFrom-Json
$plan.result.operations | Format-Table source, destination
```

Apply a previously reviewed rename plan in CI:

```bash
creator-toolkit rename ./images --yes --json > rename-result.json
```
