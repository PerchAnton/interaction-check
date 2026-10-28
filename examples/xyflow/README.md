# React Flow: replayable model sequences

An external [interaction-check](../../README.md) example for [xyflow/xyflow](https://github.com/xyflow/xyflow).
Dependencies: **@xyflow/react 12.12.0, react 19.2.0, react-dom 19.2.0**; the lockfile records transitive versions and integrity hashes.

Apply selection, position, and removal changes; ignore stale changes for a removed or unknown node.

## Run

Requires Python 3.10+ and Node 24.15+. From this repository root:

```sh
npm --prefix examples/xyflow ci --ignore-scripts --no-audit --no-fund
python examples/verify_consumers.py xyflow
```

The verifier runs 2 native/control-boundary tests and 3 passing traces / 12 steps.
Reports are written to `.artifacts/consumer-reports/` with expected and actual state.
Each event is validated; expected states remain in the Python runner and are never passed to the adapter.

## Scope and limits

This tests exported applyNodeChanges/applyEdgeChanges from @xyflow/react. It does not test ReactFlow rendering, dragging, Svelte Flow, or automatic edge deletion. Node and edge changes remain separate, as in the public helper API.

The small fixture and adapter are original example code. The installed library implements the behavior.
This is not a report of an upstream bug unless separately identified. Existing native tests are preferable
for a small single-library regression; the extra runner is useful when a sequence needs a JSON report or
must be replayed against more than one consumer/version. Upstream adoption and release credit are pending.
