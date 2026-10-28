# Huh two-field form adapter

External experimental test adapter maintained by PerchAnton. No upstream adoption is claimed.
The upstream source is fixed at `ffb6a97195b4a031925a31cc70c62fc1d309e69d` by the Go pseudo-version in go.mod; go.sum verifies fetched modules. There is no local replace directive.

Uses a real two-input Form with nonempty validation, bound values and native navigation commands. Returned Batch commands are drained sequentially; cursor ticks are allowed to finish but are not fed back. Init focuses the first field synchronously; terminal size discovery is replaced with an explicit WindowSizeMsg. This fixed fixture has no dynamic fields or hidden groups. It does not reproduce concurrent command scheduling, PTY rendering or interactive Run. Abort retains live bound values by design.

From the repository root, with Go 1.27.3 and Python 3.10+:

```sh
mkdir -p .artifacts
(cd adapters/huh && go test -race ./... && go vet ./... && go build -o ../../.artifacts/huh-probe .)
python3 interaction_check.py --timeout 30 scenarios/huh/*.json -- .artifacts/huh-probe
```

On Windows use `.exe` for the binary path. The 30-second timeout allows Huh's native blink commands to finish; it is not a performance target. Each scenario gets a fresh process.

The adapter reads events only, emits one JSON response per event, limits input records to 64 KiB and rejects unknown operations/keys. Expected state stays in the runner. Three scenarios exercise the real model. Native Go tests separately check protocol failures and request IDs.

The upstream library is MIT licensed. This adapter is MIT OR Apache-2.0, like this repository; no upstream source is copied into it.
