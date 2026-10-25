# reedline external adapter

Experimental adapter maintained by PerchAnton. Upstream adoption is not claimed.
Source: [nushell/reedline@c8d81b22](https://github.com/nushell/reedline/tree/c8d81b222745f7057a30a0fbf0ec454c5ac42e2e), pinned in the dependency file/lockfile.

Calls public LineBuffer methods without starting a shell. Covers grapheme movement/deletion, multiline joins and empty boundaries, and observes native UTF-8 byte offsets. It does not exercise ReedlineEvent dispatch, terminal rendering, completion, history or Editor undo.

## Run

Python 3.12+ is used for Python widget adapters; the runner supports Python 3.10+. Go examples use Go 1.27.3 and Rust examples use Rust 1.99.1. From the repository root:

```sh
cargo build --locked --manifest-path adapters/reedline/Cargo.toml
cargo clippy --locked --manifest-path adapters/reedline/Cargo.toml --all-targets -- -D warnings
python interaction_check.py --timeout 30 scenarios/reedline/*.json -- adapters/reedline/target/debug/interaction-check-reedline
```

On Windows append `.exe` to Rust binaries. Use a temporary virtual environment/build directory and remove it after use. 3 scenarios / 17 steps; every scenario starts a fresh adapter process. Expected states stay in the runner, never in the adapter. JSONL requests are bounded to 64 KiB. These examples supplement each project's native suite. They are not a general terminal emulator or a promise of end-to-end application coverage.
