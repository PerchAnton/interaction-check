# vee-validate: replayable model sequences

An external [interaction-check](../../README.md) example for [logaretm/vee-validate](https://github.com/logaretm/vee-validate).
Dependencies: **vee-validate 4.15.1, vue 3.5.44**; the lockfile records transitive versions and integrity hashes.

Mount a null-rendering Vue component, validate an invalid value, correct it, and reset repeatedly.

## Run

Requires Python 3.10+ and Node 24.15+. From this repository root:

```sh
npm --prefix examples/vee-validate ci --ignore-scripts --no-audit --no-fund
python examples/verify_consumers.py vee-validate
```

The verifier runs 2 native/control-boundary tests and 3 passing traces / 14 steps.
Reports are written to `.artifacts/consumer-reports/` with expected and actual state.
Each event is validated; expected states remain in the Python runner and are never passed to the adapter.

## Scope and limits

Vue setup/mount/unmount are real; the renderer host has no visible DOM. This is not a browser validation/focus test. Errors are checked with an explicit error_names array, because an empty expected object would match additional properties.

The small fixture and adapter are original example code. The installed library implements the behavior.
This is not a report of an upstream bug unless separately identified. Existing native tests are preferable
for a small single-library regression; the extra runner is useful when a sequence needs a JSON report or
must be replayed against more than one consumer/version. Upstream adoption and release credit are pending.
