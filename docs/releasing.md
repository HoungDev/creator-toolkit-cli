# Release checklist

Use this checklist for `v0.1.0` and later releases. Publishing is always a separate, manually
approved action; merging a pull request never uploads a package.

## Prepare the release

- [ ] Confirm the [trusted publishing setup](trusted-publishing.md) on PyPI, TestPyPI, and GitHub.
- [ ] Update `project.version` in `pyproject.toml`.
- [ ] Move the relevant changelog entries from **Unreleased** to a dated version section.
- [ ] Open and merge a release-preparation pull request with all required checks green.
- [ ] Build from a clean checkout with `python -m build` and run `python -m twine check dist/*`.
- [ ] Install the wheel in a fresh environment and run `creator-toolkit --help` plus one command.

## Create the version tag

From an up-to-date, clean `main` branch:

```bash
git tag -a v0.1.0 -m "Creator Toolkit CLI v0.1.0"
git push origin v0.1.0
```

Do not move or reuse a published tag. The release workflow rejects branches, malformed tags,
version mismatches, and tags whose commit is not contained in `main`.

## TestPyPI dry run

Run the workflow from the exact version tag, then approve the `testpypi` environment:

```bash
gh workflow run release.yml --ref v0.1.0 -f target=testpypi
gh run list --workflow release.yml --limit 1
```

After the run succeeds, install from TestPyPI in a fresh environment:

```bash
python -m venv .testpypi-smoke
.testpypi-smoke/bin/python -m pip install --index-url https://test.pypi.org/simple/ creator-toolkit-cli==0.1.0
.testpypi-smoke/bin/creator-toolkit --help
.testpypi-smoke/bin/creator-toolkit title "creator workflow"
```

On Windows, use `.testpypi-smoke\Scripts\python.exe` and
`.testpypi-smoke\Scripts\creator-toolkit.exe`. Do not approve production publishing until this
smoke test passes.

## Production publication

Run the same pinned workflow and approve the `pypi` environment only after reviewing the tag,
build checks, TestPyPI result, and environment deployment request:

```bash
gh workflow run release.yml --ref v0.1.0 -f target=pypi
gh run list --workflow release.yml --limit 1
```

Then verify the PyPI metadata, SHA-256 hashes, publish attestations, and a clean `pip install`.
Create the GitHub release from the existing tag only after those checks succeed.

## If a release is broken

PyPI files and version numbers are immutable. Never overwrite a file, move the tag, or reuse the
version. Instead:

1. Yank the affected release on PyPI so resolvers avoid it unless explicitly requested.
2. Mark the GitHub release and changelog with a concise impact notice and workaround.
3. Fix the problem on a new branch and publish a higher patch version through the same checklist.
4. For a security issue, coordinate through a private GitHub security advisory before disclosure.
