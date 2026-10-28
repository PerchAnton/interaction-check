# Eldiron text widget replay

This external experiment uses the actual `TheTextLineEdit` from Eldiron's
embedded `theframework` at `c1ac529b501745a38d78f633ba23d2254c2ec71c`.
It calls native Paste, Undo and Redo events and programmatic `set_value`.
Three scenarios contain 14 steps, with a native Unicode history control.

This is a headless text-widget test. It does not drive Eldiron's project rename
dialog, ProjectUndo stack, UUID selection, window, or rendered pixels. No upstream
coverage gap or adoption is claimed. The JSONL transport uses typed, bounded
events; expected states never enter the widget.

```sh
git clone --depth 1 --filter=blob:none --sparse https://github.com/markusmoenig/Eldiron .artifacts/eldiron-source
git -C .artifacts/eldiron-source fetch --depth 1 origin c1ac529b501745a38d78f633ba23d2254c2ec71c
git -C .artifacts/eldiron-source checkout c1ac529b501745a38d78f633ba23d2254c2ec71c
git -C .artifacts/eldiron-source sparse-checkout set crates/theframework
python examples/eldiron/verify_source.py
export CARGO_TARGET_DIR="$PWD/.artifacts/rust-consumers"
cargo +1.96.0 test --locked --manifest-path examples/eldiron/Cargo.toml
cargo +1.96.0 build --locked --manifest-path examples/eldiron/Cargo.toml
python examples/verify_rust_consumers.py eldiron
```

PowerShell uses `$env:CARGO_TARGET_DIR` instead of `export`. The `ui` model feature
is enabled without the framework's default GPU/window features. The Git pin and
Cargo.lock fix the source and dependency resolution. A verified sparse checkout
avoids fetching the complete game repository through Cargo. On Windows set
`git -C .artifacts/eldiron-source config core.longpaths true` before expanding the
sparse checkout if needed for the Xcode asset paths.
Ubuntu needs `libwayland-dev` and `pkg-config` for the framework's clipboard/portal
dependencies even though these scenarios do not open a window or use a clipboard.
