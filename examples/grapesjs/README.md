# GrapesJS: replayable model sequences

An external [interaction-check](../../README.md) example for [GrapesJS/grapesjs](https://github.com/GrapesJS/grapesjs).
Dependencies: **grapesjs 0.23.8, jsdom 30.1.3**; the lockfile records transitive versions and integrity hashes.

Rename a real component, undo/redo, preserve redo after an unchanged value, and replace redo with a new edit.

## Run

Requires Python 3.10+ and Node 24.15+. From this repository root:

```sh
npm --prefix examples/grapesjs ci --ignore-scripts --no-audit --no-fund
python examples/verify_consumers.py grapesjs
```

The verifier runs 2 native/control-boundary tests and 3 passing traces / 15 steps.
Reports are written to `.artifacts/consumer-reports/` with expected and actual state.
Each event is validated; expected states remain in the Python runner and are never passed to the adapter.

## Scope and limits

Runs a real headless editor with jsdom. Undo/redo pass false to operate on single stack entries; default grouped undo can combine multiple edits in one event-loop turn. This does not simulate browser gesture grouping, canvas, storage, or full UI.

The small fixture and adapter are original example code. The installed library implements the behavior.
This is not a report of an upstream bug unless separately identified. Existing native tests are preferable
for a small single-library regression; the extra runner is useful when a sequence needs a JSON report or
must be replayed against more than one consumer/version. Upstream adoption and release credit are pending.
