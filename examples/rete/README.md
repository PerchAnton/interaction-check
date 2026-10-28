# Rete.js: replayable model sequences

An external [interaction-check](../../README.md) example for [retejs/rete](https://github.com/retejs/rete).
Dependencies: **rete 2.0.6**; the lockfile records transitive versions and integrity hashes.

Cancel noderemove, connectioncreate, and clear in a real NodeEditor pipe, then retry after lifting the veto.

## Run

Requires Python 3.10+ and Node 24.15+. From this repository root:

```sh
npm --prefix examples/rete ci --ignore-scripts --no-audit --no-fund
python examples/verify_consumers.py rete
```

The verifier runs 2 native/control-boundary tests and 3 passing traces / 19 steps.
Reports are written to `.artifacts/consumer-reports/` with expected and actual state.
Each event is validated; expected states remain in the Python runner and are never passed to the adapter.

## Scope and limits

A minimal node/edge fixture uses NodeEditor directly. This does not cover renderer plugins, Rete QA, or history plugins. It does not claim that every partially cancelled clear is atomic.

The small fixture and adapter are original example code. The installed library implements the behavior.
This is not a report of an upstream bug unless separately identified. Existing native tests are preferable
for a small single-library regression; the extra runner is useful when a sequence needs a JSON report or
must be replayed against more than one consumer/version. Upstream adoption and release credit are pending.
