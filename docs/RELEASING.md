# Releases and compatibility

## Next candidate: 1.0.0 (not published)

Follow [the 1.0 checklist](RELEASE-1.0.md). Use a **new** tag matching the reviewed
package version; never reuse v0.1.0. Preparation and CI do not publish a package.


## Current non-prerelease 0.1.0

Published on 7 November 2026 through Trusted Publishing. The registry wheel and
source archive match CI, and the clean installed-wheel checks passed.
[Receipt](evidence/release-0.1.0.json) · [GitHub release](https://github.com/PerchAnton/interaction-check/releases/tag/v0.1.0).

For later releases, require the reviewed
commit to pass the full CI matrix, merge it into main and wait for main CI.
Then create a new matching version tag and use the existing Trusted Publishing
workflow with publish=true. Keep environment approval and archive checks intact.
Do not mark the release published until registry hashes and a clean installation
are verified. Publish the GitHub release with prerelease=false and attach the
exact registry artifacts and checksums. Earlier prereleases stay unchanged.

The [published 0.1.x contract](https://github.com/PerchAnton/interaction-check/blob/v0.1.0/docs/COMPATIBILITY.md) remains historical. The [candidate 1.x contract](COMPATIBILITY.md) awaits publication.

## Previous beta 0.1.0b2

Published on 5 November 2026 (Europe/Kyiv). [Package on PyPI](https://pypi.org/project/interaction-check/0.1.0b2/) · [GitHub prerelease and checksums](https://github.com/PerchAnton/interaction-check/releases/tag/v0.1.0b2) · [Installation checks](evidence/release-beta2.json).

## Previous beta.1

**[0.1.0b1 on PyPI](https://pypi.org/project/interaction-check/0.1.0b1/)** was published
on **1 November 2026 (Europe/Kyiv)** through
[Trusted Publishing](https://github.com/PerchAnton/interaction-check/actions/runs/41309451060).
The [GitHub prerelease](https://github.com/PerchAnton/interaction-check/releases/tag/v0.1.0b1)
attaches the exact checked wheel and source archive. Both match PyPI downloads.
A fresh registry install passes quickstart, dispatch and deliberate mismatch/export/replay
checks, including report schema and failure_step. [Receipt](evidence/release-beta1.json).
[The beta contract](COMPATIBILITY.md) describes additive report changes and upgrade limits.
Do not upload this version again.

## Previous published prerelease: alpha.8

**[0.1.0a8 on PyPI](https://pypi.org/project/interaction-check/0.1.0a8/)** was published
on **28 October 2026 (Europe/Kyiv)**. The
[GitHub prerelease](https://github.com/PerchAnton/interaction-check/releases/tag/v0.1.0-alpha.8)
attaches the same wheel and source archive with checksums. A fresh environment
installed the package and verified the complete quickstart, including deliberate
failure detection, original-expectation export and replay. The installed runner also
passes the real dispatch scenario and catches its deliberately wrong expectation.
The source archive passes native dispatch and Mermaid report checks.
[Hashes, installation and workflow evidence](evidence/release-alpha8.json).
Earlier registry versions, tags and release assets remain unchanged.

## Alpha compatibility

- Alpha releases are experimental. CLI options, Python APIs, report fields and
  adapter behavior may change between releases, even within `0.1.0`.
- Alpha.8 keeps scenario schema **1** and JSONL protocol **1**. This describes the
  current release; it does not promise compatibility with every future alpha.
- Pin the runner release or Git revision and the adapter/consumer revisions
  separately. Before upgrading, read the [changelog](../CHANGELOG.md) and replay
  your scenarios with their original expectations.
- Breaking changes must be called out in the changelog with migration guidance.
  Existing release tags and assets must not be replaced; fixes need a new version.

If an upgrade changes a result, [report the old and new versions with a reproducer](https://github.com/PerchAnton/interaction-check/issues/new?template=bug_report.yml).
A stable release needs experience maintaining real consumer integrations and a
compatibility contract beyond this alpha policy.

## Preparing a future release

Beta.2 and earlier prereleases each have their own immutable version and tag.
Preserve the real-property walkthrough and optional Mermaid renderer. For the next
candidate, verify the source example as well:

```sh
python -m pip install -r examples/dispatch/requirements.txt
python examples/dispatch/verify.py --check
```

The publication workflow runs those checks in the checkout and unpacked source archive.

Update the version and changelog for the new candidate, then run:

```sh
python -m unittest -v
python examples/quickstart/verify.py --report docs/evidence/quickstart.json
python tools/render_quickstart.py
python tools/render_quickstart.py --check
python -m pip install build twine
python -m build
python -m twine check --strict dist/*
python tools/check_distribution.py dist
```

`python -m build` builds the wheel from the sdist, exercising the source archive too.
The distribution check installs the wheel without an index or dependencies in a fresh
venv outside this checkout, validates metadata and version, runs a passing scenario,
exports a failing prefix, and replays it. CI repeats this on supported platforms.

Before publishing, use an empty `dist/`, review its contents, require green CI on the
exact release commit, and record SHA-256 checksums for both assets. Attach only the
verified artifacts and changelog to a prerelease pointing to that commit. Do not mark
an alpha as the latest stable release.

## Registry publication

### Earlier publication: alpha.8

`0.1.0a8` / `v0.1.0-alpha.8` is **published on PyPI**. Runtime behavior, CLI options,
scenario schema 1 and JSONL protocol 1 are unchanged from alpha.7. This release
packages the real-property walkthrough, optional Mermaid reports and clearer limits.
Publication used [workflow 40655587083](https://github.com/PerchAnton/interaction-check/actions/runs/40655587083)
and the configured `pypi` environment after the rehearsal and release-commit CI passed.
Do not rerun this version's upload; prepare a new version for any future package change.

### One-time owner setup

This setup is complete for `PerchAnton/interaction-check`. Keep these identity fields
unchanged when updating the workflow; the steps below document the configuration.

1. Sign in to the intended PyPI owner account, verify its email and enable 2FA.
2. In [Publishing](https://pypi.org/manage/account/publishing/), add a pending GitHub
   Trusted Publisher with these exact fields:

   | Field | Value |
   | --- | --- |
   | PyPI project | `interaction-check` |
   | Repository owner | `PerchAnton` |
   | Repository name | `interaction-check` |
   | Workflow filename | `publish.yml` |
   | Environment | `pypi` |

3. Create the `pypi` GitHub environment in this repository. Require owner approval
   and restrict deployments to release tags (`v*`). No PyPI API token is needed.

The pending publisher creates the project on the first successful upload. It does
not reserve its name. Account and environment setup must be completed by an owner;
these repository files do not configure either service automatically.

### Rehearsal and publication

For future candidates, run **Prepare or publish to PyPI** from `main`, with `publish=false`
(the default). The workflow tests the runner, builds wheel + sdist, checks metadata
and the installed command, and saves `pypi-distributions` with SHA-256 checksums.
It has no upload permission in this mode. Neither pushes nor PRs trigger publishing.

For an approved release, require green CI on the exact commit, create and push its
matching **new** version tag, then run the workflow from that tag with `publish=true`.
The published `v0.1.0-alpha.8` is a reference for the process, not a tag to upload again.

The build job requires a matching package version and a commit contained in `main`.
The upload job waits for the `pypi` environment, downloads the verified distributions,
checks their hashes and uses OIDC with PyPA's publishing action. Build/test jobs have
no OIDC permission. The upload job does not run project source or build scripts.
Keep PyPI attestations enabled (the action's default); do not skip duplicate uploads.

After success, verify the [project](https://pypi.org/project/interaction-check/),
version, license, Python requirement and both archive hashes. In a fresh venv:

```sh
python -m pip install --index-url https://pypi.org/simple 'interaction-check==<approved-version>'
interaction-check --version
```

Only then change the README's candidate status to published.
Keep GitHub release assets consistent with the uploaded artifacts. A failed or partial
upload must be inspected before retrying; never replace a published version's files.

References: [Python packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
and [publishing with GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/).
See also [creating a project with Trusted Publishing](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/).
