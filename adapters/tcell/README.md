# tcell external adapter

Experimental adapter maintained by PerchAnton. Upstream adoption is not claimed.
Source: [gdamore/tcell@62aecba7](https://github.com/gdamore/tcell/tree/62aecba7acc76906e342a15545ff1a8c9899d89d), pinned in the dependency file/lockfile.

Calls the current v3 CellBuffer API: Put, Resize, Fill, SetDirty and Get. Covers grapheme widths/remainders, dirty invalidation after resize and out-of-bounds writes. This is a buffer-level sequence adapter, not the v2 SimulationScreen or a terminal/input decoder test.

## Run

Python 3.12+ is used for Python widget adapters; the runner supports Python 3.10+. Go examples use Go 1.27.3 and Rust examples use Rust 1.99.1. From the repository root:

```sh
(cd adapters/tcell && go test -race ./... && go vet ./... && go build -o probe.exe .)
python interaction_check.py --timeout 30 scenarios/tcell/*.json -- adapters/tcell/probe.exe
```

On Windows append `.exe` to Rust binaries. Use a temporary virtual environment/build directory and remove it after use. 3 scenarios / 13 steps; every scenario starts a fresh adapter process. Expected states stay in the runner, never in the adapter. JSONL requests are bounded to 64 KiB. These examples supplement each project's native suite. They are not a general terminal emulator or a promise of end-to-end application coverage.
