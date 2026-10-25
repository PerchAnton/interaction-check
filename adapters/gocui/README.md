# gocui external adapter

Experimental adapter maintained by PerchAnton. Upstream adoption is not claimed.
Source: [PerchAnton/gocui@19c00ba6](https://github.com/PerchAnton/gocui/tree/19c00ba6d37ffcb9247f5e841761d4c7d9f5cc14), pinned in the dependency file/lockfile.

Uses the built-in OutputSimulator, TestingScreen and native editable view, with WaitSync synchronization. Covers editing, Unicode and a UTF-8 chunk boundary. It deliberately pins our proposed fix for [gocui #141](https://github.com/awesome-gocui/gocui/issues/141); two traces fail on the upstream pin and pass on the fork. Approval is pending. Exactly one new event is allowed per process because gocui has global screen state. A real terminal and multiple concurrent Gui instances are not covered.

## Run

Python 3.12+ is used for Python widget adapters; the runner supports Python 3.10+. Go examples use Go 1.27.3 and Rust examples use Rust 1.99.1. From the repository root:

```sh
(cd adapters/gocui && go test -race ./... && go vet ./... && go build -o probe.exe .)
python interaction_check.py --timeout 30 scenarios/gocui/*.json -- adapters/gocui/probe.exe
```

On Windows append `.exe` to Rust binaries. Use a temporary virtual environment/build directory and remove it after use. 3 scenarios / 12 steps; every scenario starts a fresh adapter process. Expected states stay in the runner, never in the adapter. JSONL requests are bounded to 64 KiB. These examples supplement each project's native suite. They are not a general terminal emulator or a promise of end-to-end application coverage.
