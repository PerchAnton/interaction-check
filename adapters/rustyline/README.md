# rustyline external adapter

Experimental adapter maintained by PerchAnton. Upstream adoption is not claimed.
Source: [kkawakam/rustyline@998cd3b9](https://github.com/kkawakam/rustyline/tree/998cd3b95b27406449fffb10199adf9fb692d809), pinned in the dependency file/lockfile.

Calls public LineBuffer methods with an original listener recording native change notifications. Covers grapheme edits, multiline joins and empty boundaries with UTF-8 byte offsets. It does not run Editor, history, undo or a PTY. The existing upstream rexpect PR #951 covers a different, complementary layer.

## Run

Python 3.12+ is used for Python widget adapters; the runner supports Python 3.10+. Go examples use Go 1.27.3 and Rust examples use Rust 1.99.1. From the repository root:

```sh
cargo build --locked --manifest-path adapters/rustyline/Cargo.toml
cargo clippy --locked --manifest-path adapters/rustyline/Cargo.toml --all-targets -- -D warnings
python interaction_check.py --timeout 30 scenarios/rustyline/*.json -- adapters/rustyline/target/debug/interaction-check-rustyline
```

On Windows append `.exe` to Rust binaries. Use a temporary virtual environment/build directory and remove it after use. 3 scenarios / 17 steps; every scenario starts a fresh adapter process. Expected states stay in the runner, never in the adapter. JSONL requests are bounded to 64 KiB. These examples supplement each project's native suite. They are not a general terminal emulator or a promise of end-to-end application coverage.
