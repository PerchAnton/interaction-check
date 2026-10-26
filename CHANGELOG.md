# Changelog

## 0.1.0a5 / v0.1.0-alpha.5

- Export each state-mismatch prefix with `--failure-dir`, without replacing expected
  states or overwriting an existing output directory. JSON reports link to saved files.
- Add a native-test handoff guide using the executable pyee and XState examples.
- Add wheel/sdist packaging and the `interaction-check` command, with zero runtime
  dependencies. `--version` works without an adapter. Python metadata/report versions
  now use the standard Python spelling `0.1.0a5` (previous report: `0.1.0-alpha.4`).
- Schema 1, JSONL protocol 1, comparison rules and adapter commands are unchanged.

Alpha releases may change CLI/report APIs. Package preparation is not registry publication.
