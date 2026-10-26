# Release preparation

The next candidate is **v0.1.0-alpha.5**; Python package metadata uses **0.1.0a5**.
The package is not yet published on PyPI. A GitHub prerelease can distribute a wheel
and source archive while the alpha CLI is evaluated. A stable release needs consumer
feedback and a documented compatibility policy beyond these experimental formats.

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

PyPI publication is a separate step: confirm the package name/account, choose a scoped
publishing method, and upload the already checked artifacts. A built wheel or GitHub
release does not establish ownership of a PyPI name. Install instructions must say
whether the package is local, from a GitHub asset, or actually available on PyPI.

References: [Python packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
and [publishing with GitHub Actions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/).
