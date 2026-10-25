# tui-input external adapter

Experimental adapter maintained by PerchAnton; upstream adoption is not claimed.
Source: [sayanarijit/tui-input](https://github.com/sayanarijit/tui-input/tree/7e615bb87db7a1611f3b00718788950defcbc2ee), pinned in Cargo.toml and Cargo.lock.

Input::handle receives native requests. Cursor positions count Unicode codepoints, movements/deletions use graphemes, and visual_cursor/visual_scroll report display columns. No terminal backend is initialized.

With Rust 1.99.1 and Python 3.10+, from the repository root:

```sh
cargo build --locked --manifest-path adapters/tui-input/Cargo.toml
cargo clippy --locked --manifest-path adapters/tui-input/Cargo.toml --all-targets -- -D warnings
python3 interaction_check.py scenarios/tui-input/*.json -- adapters/tui-input/target/debug/interaction-check-tui-input
```

Use `.exe` on Windows. Three scenarios / 16 steps; every scenario starts a fresh adapter. Expected values remain in the runner, never sent to the adapter. Input records are bounded to 64 KiB. The adapter translates events and observes state; it does not reimplement the widget.

The upstream crate is MIT licensed. This adapter is MIT OR Apache-2.0. No upstream source is copied into the adapter.
