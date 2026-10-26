# tui-textarea external adapter

Experimental adapter maintained by PerchAnton; upstream adoption is not claimed.
Source: [PerchAnton/tui-textarea](https://github.com/PerchAnton/tui-textarea/tree/1a0276461f31a57a74187d22f9d6513a9c539c37), pinned in Cargo.toml and Cargo.lock.

TextArea receives native Input events, selection and deletion operations. Cursor is [row, codepoint column]. This tests the proposed fix in [upstream PR #126](https://github.com/rhysd/tui-textarea/pull/126), not upstream main: all three traces fail on upstream 4d18622eeac13b309e0ff6a55a46ac6706da68cf and pass on the pinned fix. The host bug is reported in issue #121. No renderer, terminal or clipboard is exercised.

With Rust 1.99.1 and Python 3.10+, from the repository root:

```sh
cargo build --locked --manifest-path adapters/tui-textarea/Cargo.toml
cargo clippy --locked --manifest-path adapters/tui-textarea/Cargo.toml --all-targets -- -D warnings
python3 interaction_check.py scenarios/tui-textarea/*.json -- adapters/tui-textarea/target/debug/interaction-check-tui-textarea
```

Use `.exe` on Windows. Three scenarios / 14 steps; every scenario starts a fresh adapter. Expected values remain in the runner, never sent to the adapter. Input records are bounded to 64 KiB. The adapter translates events and observes state; it does not reimplement the widget.

The upstream crate is MIT licensed. This adapter is MIT OR Apache-2.0. No upstream source is copied into the adapter.
