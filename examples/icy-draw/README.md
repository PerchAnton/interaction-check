# Icy Draw engine with an edit-session guard

This external experiment uses the actual `icy_engine_edit` commands and undo
history from `mkrueger/icy_tools` at `9ebe3dea322433c576b2a9e98c20490673b2fbd7`,
plus edit-session at `968ebd2f9a9b04c068b34a3fba42c246261380b7`.
It stages a layer name, applies a changed confirmation through
`EditState::update_layer_properties`, skips an unchanged confirmation, and rejects
a draft after an intervening edit/undo. The host still owns all history entries.

The fixture has one document and one layer. Its `(document, layer, generation)`
identity and generation increments are supplied by this adapter; the upstream
dialog has not been changed. This is not a reusable identity implementation for
multiple documents or layer removal, nor a GUI test. `Direct` explicitly bypasses
the draft guard to represent an intervening host command.

Three scenarios contain 23 steps: cancellation and one-shot confirmation,
no-op confirmation preserving Redo, and an edit/undo invalidating an open draft
even when the visible name has returned to its original value.

```sh
export CARGO_TARGET_DIR="$PWD/.artifacts/rust-consumers"
cargo +1.96.0 test --locked --manifest-path examples/icy-draw/Cargo.toml
cargo +1.96.0 build --locked --manifest-path examples/icy-draw/Cargo.toml
python examples/verify_rust_consumers.py icy-draw
```

PowerShell uses `$env:CARGO_TARGET_DIR` instead of `export`. The engine is built
without its default UI feature. The JSONL transport has bounded, typed events;
expected states remain in the runner. No upstream defect or dependency acceptance
is implied by these normal traces.
