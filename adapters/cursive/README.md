# Cursive EditView adapter

External experimental adapter maintained by PerchAnton; no upstream adoption is claimed.
Uses cursive_core at commit `9250e09c00b0c94b216178d07e45bd79b317dcec`, with default features disabled and Cargo.lock committed. No terminal backend is needed.

Text/key events go through the actual `View::on_event`, callbacks through `EventResult::process` and resize through `View::layout`. The submitted values come from the real EditView callback. Cursor positions are UTF-8 **byte offsets**; moving/deleting graphemes is Cursive's behavior, not adapter logic. Explicit cursor setters validate byte boundaries before calling the native API. The adapter does not test terminal rendering, mouse input or focus routing between views.

From the repository root with Rust 1.99.1 and Python 3.10+:

```sh
cargo build --locked --manifest-path adapters/cursive/Cargo.toml
cargo clippy --locked --manifest-path adapters/cursive/Cargo.toml --all-targets -- -D warnings
python3 interaction_check.py scenarios/cursive/*.json -- adapters/cursive/target/debug/interaction-check-cursive
```

On Windows the binary ends in `.exe`. Three scenarios cover Unicode/grapheme editing, resizing and submit callbacks. Each gets a fresh process; expectations are never sent to the adapter.

Cursive is MIT licensed. This adapter is MIT OR Apache-2.0; no upstream source is copied into it.
