# rat-salsa external adapter

Experimental adapter maintained by PerchAnton. Upstream adoption is not claimed.
Source: [thscharler/rat-salsa@5162d979](https://github.com/thscharler/rat-salsa/tree/5162d97926ff95ac197f2013dcd9cf57082f0f2a), pinned in the dependency file/lockfile.

Calls rat-text TextInputState methods. Covers graphemes, explicitly grouped selection replacement and no-op redo. The begin_group/end_group events call the documented UndoBuffer.begin_seq/end_seq API; grouping is not invented by the adapter. Cursor positions count graphemes. No clipboard, renderer, focus routing or terminal is exercised.

## Run

Python 3.12+ is used for Python widget adapters; the runner supports Python 3.10+. Go examples use Go 1.27.3 and Rust examples use Rust 1.99.1. From the repository root:

```sh
cargo build --locked --manifest-path adapters/rat-salsa/Cargo.toml
cargo clippy --locked --manifest-path adapters/rat-salsa/Cargo.toml --all-targets -- -D warnings
python interaction_check.py --timeout 30 scenarios/rat-salsa/*.json -- adapters/rat-salsa/target/debug/interaction-check-rat-salsa
```

On Windows append `.exe` to Rust binaries. Use a temporary virtual environment/build directory and remove it after use. 3 scenarios / 18 steps; every scenario starts a fresh adapter process. Expected states stay in the runner, never in the adapter. JSONL requests are bounded to 64 KiB. These examples supplement each project's native suite. They are not a general terminal emulator or a promise of end-to-end application coverage.
