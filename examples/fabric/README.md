# Fabric.js: replayable model sequences

An external [interaction-check](../../README.md) example for [fabricjs/fabric.js](https://github.com/fabricjs/fabric.js).
Dependencies: **fabric 7.4.0**; the lockfile records transitive versions and integrity hashes.

Move a real Group, detach and re-add objects, and preserve their scene centers. A detached object must not move with its former group.

## Run

Requires Python 3.10+ and Node 24.15+. From this repository root:

```sh
npm --prefix examples/fabric ci --ignore-scripts --no-audit --no-fund
python examples/verify_consumers.py fabric
```

The verifier runs 2 native/control-boundary tests and 3 passing traces / 11 steps.
Reports are written to `.artifacts/consumer-reports/` with expected and actual state.
Each event is validated; expected states remain in the Python runner and are never passed to the adapter.

## Scope and limits

Uses real Rect/Group geometry without a canvas. Rendering, pointer selection, text, and editor history are outside this example. Rounded coordinates use a 1e-6 precision for the small integer fixture.

The small fixture and adapter are original example code. The installed library implements the behavior.
This is not a report of an upstream bug unless separately identified. Existing native tests are preferable
for a small single-library regression; the extra runner is useful when a sequence needs a JSON report or
must be replayed against more than one consumer/version. Upstream adoption and release credit are pending.
