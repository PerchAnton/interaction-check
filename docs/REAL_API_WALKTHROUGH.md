# What an adapter does: rat-salsa

The [rat-salsa question](https://github.com/thscharler/rat-salsa/issues/36#issuecomment-6461513249)
was about what we proposed: an optional external reproduction maintained by us.
It does not justify an upstream dependency or CI change.

The existing [five-step case](https://github.com/PerchAnton/interaction-check/blob/055dfc24a4eda7478719dcbbb1f0ac123176aec9/scenarios/rat-salsa/03-empty-noop-redo.json)
calls a real `rat_text::text_input::TextInputState` through this
[Rust adapter](https://github.com/PerchAnton/interaction-check/blob/055dfc24a4eda7478719dcbbb1f0ac123176aec9/adapters/rat-salsa/src/main.rs):

| JSON event | Actual API | Expected `value` |
| --- | --- | --- |
| `{"op":"new","text":""}` | `TextInputState::new()`, `set_text("")` | `""` |
| `{"op":"text","text":"x"}` | `insert_str("x")` | `"x"` |
| `{"op":"key","key":"undo"}` | `undo()` | `""` |
| `{"op":"key","key":"backspace"}` | `delete_prev_char()` | `""` |
| `{"op":"key","key":"redo"}` | `redo()` | `"x"` |

The adapter returns `buffer.text()` after each action, alongside cursor/selection.
A hypothetical failure on the last step would report `state.value: expected 'x', got ''`.
This illustrates the report shape, **not a newly reproduced rat-salsa bug**. The adapter
and lockfile are on the linked historical evaluation revision; PyPI does not install them.

For a current-source example that you can run and see fail deliberately, use
[JSON → python-dispatch → callbacks](../examples/dispatch/README.md). Its verifier
checks the first mismatch and produces expected/observed diagrams without a Rust toolchain.

## Why not a normal Rust test?

A native test can call those same five methods and assert `buffer.text() == "x"`.
That is preferred for a single regression. Replay adds Python, a JSONL adapter,
scenario maintenance and startup/serialization cost. It helps only if sharing a case
**within that adapter's contract** makes reproduction or revision comparison easier.

The methods do not exercise terminal rendering, focus routing, OS keyboard events,
clipboard or an application's integration. They establish neither additional coverage
nor faster tests. All actions may already have run before the first mismatch is reported;
exporting a checked prefix does not undo effects.

For pyee, the proposed behavior is already in the existing
[native-test PR #228](https://github.com/jfhbrook/pyee/pull/228). A new runner dependency
and a duplicate PR are unnecessary. Acceptance and adoption remain separate from
passing external examples.
