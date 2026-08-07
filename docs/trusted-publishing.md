# Trusted publishing setup

Creator Toolkit publishes without stored PyPI API tokens. The release workflow exchanges a
GitHub OpenID Connect identity for a short-lived PyPI credential, and the publish job is isolated
from the build job.

This is a one-time maintainer setup. It does not publish a package.

## 1. Protect the GitHub environments

Create two repository environments under **Settings > Environments**:

| Environment | Required reviewer | Allowed deployment tags |
| --- | --- | --- |
| `testpypi` | A trusted maintainer | `v*.*.*` |
| `pypi` | A trusted maintainer | `v*.*.*` |

Require approval for both environments. A solo maintainer may leave "prevent self-review" off;
projects with another trusted maintainer should enable it. Do not add PyPI passwords, API tokens,
or other publishing secrets to either environment.

## 2. Register the pending publishers

The `creator-toolkit-cli` project does not yet exist on either package index. Sign in to each
index, open the account-level **Publishing** page, and add a pending GitHub publisher with these
exact values:

| Setting | PyPI | TestPyPI |
| --- | --- | --- |
| Project name | `creator-toolkit-cli` | `creator-toolkit-cli` |
| Owner | `HoungDev` | `HoungDev` |
| Repository | `creator-toolkit-cli` | `creator-toolkit-cli` |
| Workflow filename | `release.yml` | `release.yml` |
| Environment | `pypi` | `testpypi` |

- [PyPI pending publisher settings](https://pypi.org/manage/account/publishing/)
- [TestPyPI pending publisher settings](https://test.pypi.org/manage/account/publishing/)
- [Official pending publisher documentation](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)

A pending publisher does not reserve the package name. Recheck availability immediately before
the first release, and make sure the project name exactly matches `project.name` in
`pyproject.toml`.

## 3. Verify the trust boundary

Before the first run, confirm all of the following:

- `.github/workflows/release.yml` is the only workflow registered with either package index.
- The publisher environment name exactly matches `pypi` or `testpypi`; whitespace matters.
- Only the publish job has `id-token: write`.
- The publish job only downloads the previously built artifact and invokes the pinned PyPA action.
- Environment deployment rules restrict releases to `v*.*.*` tags.

As an additional defense, add a repository tag ruleset for `v*` that limits tag creation to
maintainers and blocks tag updates or deletion. Verify its bypass list before enabling it so the
maintainer who performs releases is not accidentally locked out.

The action generates and uploads PyPI publish attestations by default. Review the trusted
publisher configuration whenever the repository, workflow file, environments, or maintainer
access changes.
