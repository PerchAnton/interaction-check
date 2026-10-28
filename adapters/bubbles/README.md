# Bubbles textinput adapter

External experimental test adapter maintained by PerchAnton. No upstream adoption is claimed.
The upstream source is fixed at `c3bde0d166c2ca607d9864493453fd77bdcae7e4` by the Go pseudo-version in go.mod; go.sum verifies fetched modules. There is no local replace directive.

Uses the real textinput.Model.Update, View and cursor/focus/width APIs. Cursor offsets are **runes**, not bytes or terminal columns. Virtual cursor timing and clipboard commands are excluded; this is not a terminal/PTY test.

From the repository root, with Go 1.27.3 and Python 3.10+:

```sh
mkdir -p .artifacts
(cd adapters/bubbles && go test -race ./... && go vet ./... && go build -o ../../.artifacts/bubbles-probe .)
python3 interaction_check.py --timeout 30 scenarios/bubbles/*.json -- .artifacts/bubbles-probe
```

On Windows use `.exe` for the binary path. The 30-second timeout allows Huh's native blink commands to finish; it is not a performance target. Each scenario gets a fresh process.

The adapter reads events only, emits one JSON response per event, limits input records to 64 KiB and rejects unknown operations/keys. Expected state stays in the runner. Three scenarios exercise the real model. Native Go tests separately check protocol failures and request IDs.

The upstream library is MIT licensed. This adapter is MIT OR Apache-2.0, like this repository; no upstream source is copied into it.
