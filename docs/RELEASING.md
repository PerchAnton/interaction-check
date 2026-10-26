# Releases and alpha compatibility

## Published prerelease

**[v0.1.0-alpha.5](https://github.com/PerchAnton/interaction-check/releases/tag/v0.1.0-alpha.5)**
was published on **26 October 2026**, with a wheel, source archive and SHA-256
checksums. Python package metadata and `--version` use **0.1.0a5**. The package is
not published on PyPI. See the [installation instructions](../README.md#install-the-released-command).

## Alpha compatibility

- Alpha releases are experimental. CLI options, Python APIs, report fields and
  adapter behavior may change between releases, even within `0.1.0`.
- Alpha.5 keeps scenario schema **1** and JSONL protocol **1**. This describes the
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

Update the version and changelog for the new candidate, then run:

```sh
python -m unittest -v
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
an alpha as the latest stable release. No automated registry upload is configured.

## Registry publication

PyPI publication is a separate step: confirm the package name/account, choose a scoped
publishing method, and upload the already checked artifacts. A built wheel or GitHub
release does not establish ownership of a PyPI name. Install instructions must say
whether the package is local, from a GitHub asset, or actually available on PyPI.

References: [Python packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
and [publishing with GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/).
