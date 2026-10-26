# diagram-js: replayable model sequences

An external [interaction-check](../../README.md) example for [bpmn-io/diagram-js](https://github.com/bpmn-io/diagram-js).
Dependencies: **diagram-js 15.28.1, didi 11.0.1**; the lockfile records transitive versions and integrity hashes.

Execute, undo, redo, reject, and branch commands using the real CommandStack, EventBus, and dependency injector.

## Run

Requires Python 3.10+ and Node 24.15+. From this repository root:

```sh
npm --prefix examples/diagram-js ci --ignore-scripts --no-audit --no-fund
python examples/verify_consumers.py diagram-js
```

The verifier runs 2 native/control-boundary tests and 3 passing traces / 15 steps.
Reports are written to `.artifacts/consumer-reports/` with expected and actual state.
Each event is validated; expected states remain in the Python runner and are never passed to the adapter.

## Scope and limits

The original value.set command is a fixture, not a diagram-js modeling feature. The caller explicitly checks canExecute: execute does not perform that policy check. No canvas renderer or BPMN model is tested.

The small fixture and adapter are original example code. The installed library implements the behavior.
This is not a report of an upstream bug unless separately identified. Existing native tests are preferable
for a small single-library regression; the extra runner is useful when a sequence needs a JSON report or
must be replayed against more than one consumer/version. Upstream adoption and release credit are pending.
