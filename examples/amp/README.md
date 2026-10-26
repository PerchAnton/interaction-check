# Amp command replay experiment

This optional external test bridge calls Amp's real buffer commands at revision
`df97a3c01e6021a464af4204dd64d10eb205f149`. It is compiled inside Amp's existing
`cfg(test)` library and uses its own `TestTerminal`. It does not launch a terminal
UI, change Amp's release binary, or test rendering, keyboard decoding, or modes.

`prepare.py` requires a clean, disposable checkout at that exact revision. It
adds only the test module and its dependencies and copies the pinned Cargo.lock.
Do not run it on a checkout with your work. The bridge has a native Unicode
undo/redo control and three normal JSON traces (14 steps) covering Unicode backspace,
empty backspace, and replacing a redo branch. Linux CI is the validation target;
Amp's terminal dependencies do not support a native Windows build.

From the interaction-check root on Linux, with Rust 1.96 installed:

```sh
git clone https://github.com/jmacdonald/amp .artifacts/amp-source
git -C .artifacts/amp-source checkout df97a3c01e6021a464af4204dd64d10eb205f149
python examples/amp/prepare.py .artifacts/amp-source
export CARGO_TARGET_DIR="$PWD/.artifacts/amp-target"
cargo +1.96.0 test --locked --manifest-path .artifacts/amp-source/Cargo.toml --no-run --lib --message-format=json > .artifacts/amp-build.jsonl
python examples/amp/verify.py --source .artifacts/amp-source --build-log .artifacts/amp-build.jsonl
```

Ubuntu needs `libxcb1-dev libxcb-render0-dev libxcb-shape0-dev libxcb-xfixes0-dev`
and `pkg-config`. The Python wrapper removes only libtest's known startup banner
and validates the response envelope; it never supplies expected states to Amp.
The shared Rust protocol limits input to 64 KiB per line and 1,024 events.
The adapter limits input text and the buffer and supports single-line fixtures.
The normal branch trace explicitly calls the native Home command after Undo.
A separate regression preserves the original direct-command sequence without
Home: insert `a`, undo, then insert `b` leaves the buffer empty at step 4.
The verifier requires that exact known failure, separately from passing traces.
This is an observed command-level result at the pin, not a claimed GUI reproduction
or an upstream fix. Direct buffer insertion does not adjust a stale cursor after
Undo. The adapter must not silently supply cursor movement that the trace omitted.

The existing Amp native suite remains the source of truth; this experiment
demonstrates a portable event sequence and step report, not missing upstream coverage.
