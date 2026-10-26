# Changelog

## 0.1.0a6 / v0.1.0-alpha.6 — unpublished candidate

- Prepare PyPI metadata, installation instructions and a manual Trusted Publishing
  workflow. Its default mode builds and checks packages without uploading them.
- Publish only from a matching version tag, with separate build and upload jobs.
- CLI/report version advances to `0.1.0a6`; schema 1, protocol 1 and runtime behavior
  are unchanged from alpha.5. Existing GitHub archives and tags remain unchanged.

## 0.1.0a5 / v0.1.0-alpha.5

- Export each state-mismatch prefix with `--failure-dir`, without replacing expected
  states or overwriting an existing output directory. JSON reports link to saved files.
- Add a native-test handoff guide using the executable pyee and XState examples.
- Add wheel/sdist packaging and the `interaction-check` command, with zero runtime
  dependencies. `--version` works without an adapter. Python metadata/report versions
  now use the standard Python spelling `0.1.0a5` (previous report: `0.1.0-alpha.4`).
- Schema 1, JSONL protocol 1, comparison rules and adapter commands are unchanged.

Published as a GitHub prerelease on 26 October 2026; not published on PyPI.
See the [alpha compatibility policy](docs/RELEASING.md#alpha-compatibility) before upgrading.
