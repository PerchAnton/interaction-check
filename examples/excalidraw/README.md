# Excalidraw: replayable model sequences

An external [interaction-check](../../README.md) example for [excalidraw/excalidraw](https://github.com/excalidraw/excalidraw).
Dependencies: **@excalidraw/excalidraw 0.18.1, @napi-rs/canvas 1.0.13, jsdom 30.1.3, react 18.3.1, react-dom 18.3.1**; the lockfile records transitive versions and integrity hashes.

Convert real elements, mutate coordinates, preserve versions on no-op changes, and restore saved/deleted geometry.

## Run

Requires Python 3.10+ and Node 24.15+. From this repository root:

```sh
npm --prefix examples/excalidraw ci --ignore-scripts --no-audit --no-fund
python examples/verify_consumers.py excalidraw
```

The verifier runs 2 native/control-boundary tests and 3 passing traces / 12 steps.
Reports are written to `.artifacts/consumer-reports/` with expected and actual state.
Each event is validated; expected states remain in the Python runner and are never passed to the adapter.

## Scope and limits

Uses the public element APIs from the npm package, bundled locally by esbuild. jsdom supplies DOM constructors and @napi-rs/canvas supplies a real Canvas2D engine required during library initialization. The adapter does not resize canvases, render React, simulate pointer input, test history, or establish rendering parity. Generated third-party bundles stay in .artifacts and are not committed. The verifier builds the bundle before tests.

The small fixture and adapter are original example code. The installed library implements the behavior.
This is not a report of an upstream bug unless separately identified. Existing native tests are preferable
for a small single-library regression; the extra runner is useful when a sequence needs a JSON report or
must be replayed against more than one consumer/version. Upstream adoption and release credit are pending.
