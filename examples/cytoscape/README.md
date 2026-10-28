# Cytoscape.js: replayable model sequences

An external [interaction-check](../../README.md) example for [cytoscape/cytoscape.js](https://github.com/cytoscape/cytoscape.js).
Dependencies: **cytoscape 3.34.4**; the lockfile records transitive versions and integrity hashes.

Remove a node and its incident edge twice, restore selection, and restore a reversed edge. Observations come from real collections and add/remove/select events.

## Run

Requires Python 3.10+ and Node 24.15+. From this repository root:

```sh
npm --prefix examples/cytoscape ci --ignore-scripts --no-audit --no-fund
python examples/verify_consumers.py cytoscape
```

The verifier runs 2 native/control-boundary tests and 3 passing traces / 13 steps.
Reports are written to `.artifacts/consumer-reports/` with expected and actual state.
Each event is validated; expected states remain in the Python runner and are never passed to the adapter.

## Scope and limits

No renderer, layout, mouse input, or application history is exercised. Existing native collection tests already cover related behavior.

The small fixture and adapter are original example code. The installed library implements the behavior.
This is not a report of an upstream bug unless separately identified. Existing native tests are preferable
for a small single-library regression; the extra runner is useful when a sequence needs a JSON report or
must be replayed against more than one consumer/version. Upstream adoption and release credit are pending.
