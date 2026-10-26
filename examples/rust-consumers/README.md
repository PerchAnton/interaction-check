# Rust consumer models

Four external experiments use real upstream crates at immutable Git revisions. They do not modify the upstream applications or claim GUI coverage. Cargo.lock pins the transitive resolution. Rust 1.96 is required by the current Xilem Core source.

| Consumer | Revision | What is exercised | Traces / steps |
|---|---|---|---|
| Floem reactive | `1351ffb162faeb8be983f1301d718a0d5fb59c27` | A real effect, batched updates, dynamic dependency removal, and scope disposal/recreation | 3 / 13 |
| Helix core | `ba40e547426b0f9896c8bdc699a4ab11f2b37dbc` | Real Unicode transactions and History inversions, current redo branch, and history boundaries | 3 / 15 |
| Microsoft Edit | `cb6de0a8966aecd01d19a3541dab1829d0e679ca` | TextBuffer writes, byte cursor positions, clean markers, undo/redo, and CRLF normalization | 3 / 15 |
| Xilem Core | `271a27a6d4a930f7878d404f9014e3c50a3a9b88` | Option<ViewSequence> lifecycle and rejection of messages addressed to a removed incarnation | 3 / 20 |

Run from the repository root (PowerShell: set `$env:CARGO_TARGET_DIR` instead of `export`):

```sh
export CARGO_TARGET_DIR="$PWD/.artifacts/rust-consumers"
cargo +1.96.0 test --locked --manifest-path examples/rust-consumers/Cargo.toml --workspace
cargo +1.96.0 build --locked --manifest-path examples/rust-consumers/Cargo.toml --workspace
python examples/verify_rust_consumers.py floem
python examples/verify_rust_consumers.py helix
python examples/verify_rust_consumers.py microsoft-edit
python examples/verify_rust_consumers.py xilem
```

On Linux, Microsoft Edit needs ICU shared libraries (`libicu-dev` on Ubuntu). No grammar downloads, terminal UI, window, or GPU is used. The four binaries use the bounded JSONL transport in `protocol`: 64 KiB lines, 1,024 events, bounded text and indices, typed events, and no expected-state input. Native controls and adapter boundary tests are included; they run without the Python runner.

Floem uses its reactive crate, not its list/focus harness. Helix uses core transactions/history, not modal commands or multiple selections; the adapter supplies a point selection only for storing the original revision. Microsoft Edit's `write_raw` still normalizes newlines according to `set_crlf(false)`, and `mark_as_clean` does not write a file. Xilem uses an original no-element Pulse fixture; generation routing, rebuild, and stale-message decisions are implemented by the real `Option<ViewSequence>`. It does not use Masonry TextInput or render widgets.

These tests demonstrate an optional portable report format. They do not establish missing upstream coverage, acceptance of a dependency, or a performance improvement over native tests.
