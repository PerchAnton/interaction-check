# tview external adapter

Experimental adapter maintained by PerchAnton; no upstream adoption is claimed. tview is pinned to `c15b79fa47f27032f26647a75cb5a81720255076` by its Go pseudo-version and go.sum.

Keys go through the real InputField.InputHandler. Acceptance, changed and done callbacks are the native callbacks. Draw uses a tcell SimulationScreen: a memory-only screen, not a user's terminal. This covers basic layout during resize but not PTY escape sequences, OS input, concurrent Application.Run or focus traversal between controls.

From the root with Go 1.27.3 and Python 3.10+:

```sh
mkdir -p .artifacts
(cd adapters/tview && go test -race ./... && go vet ./... && go build -o ../../.artifacts/tview-probe .)
python3 interaction_check.py scenarios/tview/*.json -- .artifacts/tview-probe
```

Use `.exe` on Windows. Three scenarios / 15 steps cover Unicode editing, rejected input without changed callbacks, resize and completion keys. The fixture's digits-only validator is illustrative application policy. Expected values are never sent to the adapter. Protocol tests independently reject malformed requests.

tview/tcell are MIT and Apache-2.0 licensed respectively. This adapter is MIT OR Apache-2.0; it does not copy upstream source.
