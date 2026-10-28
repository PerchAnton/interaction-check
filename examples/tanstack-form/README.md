# TanStack Form: replayable model sequences

An external [interaction-check](../../README.md) example for [TanStack/form](https://github.com/TanStack/form).
Dependencies: **@tanstack/form-core 1.33.5**; the lockfile records transitive versions and integrity hashes.

Run normal form-level validation and reset after completion. A separate deterministic deferred-promise trace reproduces stale errors after reset while validation is pending.

## Run

Requires Python 3.10+ and Node 24.15+. From this repository root:

```sh
npm --prefix examples/tanstack-form ci --ignore-scripts --no-audit --no-fund
python examples/verify_consumers.py tanstack-form
```

The verifier runs 2 native/control-boundary tests and 2 passing traces / 9 steps.
Reports are written to `.artifacts/consumer-reports/` with expected and actual state.
Each event is validated; expected states remain in the Python runner and are never passed to the adapter.

The verifier also requires the separate reset regression to fail at the documented step with the old error. A crash, timeout, protocol error, or earlier mismatch does not count as reproducing it.

## Scope and limits

The known regression intentionally FAILS at step 5 on 1.33.5. It is not counted among passing scenarios. Related upstream work: #2381/#2382 (field reset), #2350/#2440 (aborted form results). No claim of a new unreported bug or a fixed upstream version. Validation status has separate timing/accounting behavior; the reset regression asserts values and errors, not that flag.

The small fixture and adapter are original example code. The installed library implements the behavior.
This is not a report of an upstream bug unless separately identified. Existing native tests are preferable
for a small single-library regression; the extra runner is useful when a sequence needs a JSON report or
must be replayed against more than one consumer/version. Upstream adoption and release credit are pending.
