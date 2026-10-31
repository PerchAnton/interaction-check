# A Rust API case, with and without replay

This external example pins tui-input at
[`7e615bb`](https://github.com/sayanarijit/tui-input/tree/7e615bb87db7a1611f3b00718788950defcbc2ee).
It is maintained here, not installed by PyPI or adopted by tui-input. The source
archive includes it; the published alpha.8 archive predates this walkthrough.

From this repository, with Python 3.10+ and Rust 1.99.1 available:

```sh
python examples/tui-input/verify.py
```

Cargo fetches the pinned Rust dependency and locked transitive dependencies on the
first run. The Python runner uses only its standard library. The verifier runs
the native test, builds the adapter, checks the correct JSON, then changes one
expectation in a temporary copy and verifies the first mismatch and its export.
An expected `FAIL` is followed by `Verified`; the verifier itself exits 0.

## Actions and states

The input contains `x`, `e` plus combining acute accent, and `界`:

| Step | Actual tui-input call | Expected returned state |
| --- | --- | --- |
| 1 | `Input::new("xe\u{301}界".into())` | value `xé界`, cursor 4 codepoints, visual cursor 4 columns |
| 2 | `handle(GoToPrevChar)` | cursor 3, visual cursor 2 |
| 3 | `handle(GoToPrevChar)` | cursor 1, visual cursor 1 |
| 4 | `handle(DeleteNextChar)` | value `x界`, cursor 1 |

The real calls and assertions are in [native.rs](tests/native.rs). The matching
action/expectation pairs are in [graphemes.json](graphemes.json). The adapter
receives only events, never expected values; its output includes actual text,
codepoint cursor, calculated visual cursor, scroll columns and width. Expectations
may check a subset of those fields.

```sh
cargo test --locked --manifest-path examples/tui-input/Cargo.toml --test native
cargo build --locked --manifest-path examples/tui-input/Cargo.toml
python interaction_check.py --trace --report result.json \
  examples/tui-input/graphemes.json -- \
  examples/tui-input/target/debug/interaction-check-tui-input
```

Use the `.exe` executable on Windows; a custom `CARGO_TARGET_DIR` changes its path.
The verifier resolves that path through Cargo metadata.

Changing only the final expected value to `xé界` deliberately produces:

```text
Step 4
state.value: expected 'xé界', got 'x界'
```

This is a wrong expectation illustrating diagnosis, **not an upstream defect**.
`--failure-dir failures` exports the original expectations through that mismatch.
The verifier reruns the export. The runner may have executed the entire batch
before comparing states; the first mismatch is not a guarantee of early stopping
or automatic minimization.

## What does the extra machinery buy?

```text
JSON actions → Python runner → JSONL Rust adapter → Input::handle
JSON expectations ← Python comparison ← actual value/cursor from Rust
```

For this one regression, prefer the short ordinary Rust test. It needs tui-input
and Cargo, but no Python runner, JSON parser/serializer or separate adapter. Replay
adds Python at development/CI time, serde/serde_json in this adapter, another
executable, protocol and scenario maintenance, and process/serialization overhead.
It adds no dependency to an application unless its owner chooses to integrate it.

The concrete extra artifact is a data-only action sequence, expected/actual trace
and checked prefix that another user of **this same adapter contract** can rerun.
That may help exchange reproductions or compare pinned revisions. Rust tests can
also be shared and produce good assertion reports. This example does not prove
better coverage, faster tests, less maintenance or net benefit for tui-input.

Calculated cursor columns are not a terminal screenshot. This adapter does not
test rendered cells, real key delivery, terminal modes, focus routing, clipboard,
or an application's event loop. Native terminal-buffer tests and interactive
examples remain appropriate for those needs. A passing state replay cannot replace
them. Maintainers may reasonably decide the extra runner is not worthwhile.
