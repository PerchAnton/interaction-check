# interaction-check

**Experimental, 0.1.0-alpha.3.** An independent development tool for replaying semantic
interaction traces against an explicit local adapter. No third-party Python packages.
Maintained by [PerchAnton](https://github.com/PerchAnton); no PyPI release or upstream adoption.

The first adapter uses the independent [edit-session library](https://github.com/PerchAnton/edit-session)
from a fixed Git revision, and commits through PhotoCraft's actual `Session` command API.
The tool itself knows nothing about opacity, PDF geometry, Rust, Go or a GUI framework.
Consumer-owned adapters now also exercise the real PhotoCraft and PdfCraft dialogs.

## Proposed PhotoCraft UI consumer

[PhotoCraft PR #9190](https://github.com/storytold/photocraft/pull/9190) adds a PhotoCraft-owned
adapter that drives the shipped Edit Selected Guides dialog, egui canvas/dialog frames, control
field setter and real Session. Its CI fetches this runner at
`f8d4282d61576ffe78d18553c642d215887e2d9f`; Python is not an application runtime dependency.
[Ten scenarios / 44 steps](https://github.com/PerchAnton/photocraft/tree/46b4a183d5f44035bbc216dcf6196701bcb45bc9/tests/interactions/guide-edit)
pass locally, covering preview, commit, Cancel/Escape, invalid input, no-ops and stale drafts.
This consumer patch is awaiting maintainer review; upstream adoption is not claimed.

## Proposed PdfCraft UI consumer

[PdfCraft PR #4594](https://github.com/storytold/pdfcraft/pull/4594) uses this runner for **Document Properties**.
Its runtime draft lifecycle uses edit-session; this runner checks the resulting UI and engine state.
Description, Initial View and Custom values share a draft bound to document identity,
edit generation and permissions. `check_live` rejects stale input after edits, Undo/Redo,
reload or a document switch; the existing engine commits one atomic batch. Cancel,
Escape and no-ops do not add history. Failed engine edits retain the form for correction.
Clean inspection tabs retain their existing live refresh without rebasing typed input.

The consumer owns a [real UI adapter](https://github.com/PerchAnton/pdfcraft/blob/535d990d10832baf3b0a64910c51b280c224bd5c/crates/ui-egui/examples/properties_scenarios.rs)
and [10 scenarios / 79 steps](https://github.com/PerchAnton/pdfcraft/tree/535d990d10832baf3b0a64910c51b280c224bd5c/tests/interactions/document-properties),
replayed by interaction-check, including save/reopen and preservation of custom metadata.
Local scoped UI tests, strict Clippy, assets, parity and wasm checks pass. Both dependencies
are pinned; upstream review of the source-policy exception and adoption is pending.
See [reproduction instructions](https://github.com/PerchAnton/pdfcraft/blob/535d990d10832baf3b0a64910c51b280c224bd5c/docs/document-properties-sessions.md).

## External widget adapters

| Consumer | Scope | Scenarios |
| --- | --- | --- |
| [Bubbles](adapters/bubbles/README.md) | Real textinput update/layout, Unicode rune cursor, focus and resize | 3 / 20 steps |
| [Huh](adapters/huh/README.md) | Real two-field form, validation, Tab/Shift+Tab, submit and abort | 3 / 19 steps |
| [Cursive](adapters/cursive/README.md) | Real EditView, UTF-8 byte cursor, graphemes, layout and callbacks | 3 / 17 steps |
| [tview](adapters/tview/README.md) | Real InputField callbacks and tcell SimulationScreen | 3 / 15 steps |
| [tui-input](adapters/tui-input/README.md) | Native requests, grapheme editing, codepoint and display-column positions | 3 / 16 steps |
| [tui-textarea](adapters/tui-textarea/README.md) | Native selection/deletion/Undo/Redo; proposed #121 fix | 3 / 14 steps |

These are external prototypes, not accepted upstream integrations. The tui-textarea adapter
pins our proposed [fix #126](https://github.com/rhysd/tui-textarea/pull/126); all three
traces fail on upstream main and pass on the patch. It is not a claim that upstream main is fixed. Preliminary discussions
are [Bubbles #1076](https://github.com/charmbracelet/bubbles/discussions/1076) and
[Huh #838](https://github.com/charmbracelet/huh/discussions/838). Each adapter has its own
pinned dependencies, documented boundary and replay instructions. No runtime integration
with the runner is needed by the upstream project.

## Run

Requires Python 3.10+ (tested with Python 3.14 on macOS arm64).

```sh
python3 -m unittest -v
cargo build --locked --manifest-path adapters/photocraft/Cargo.toml
python3 interaction_check.py --report result.json --junit result.xml scenarios/photocraft/*.json -- \
  adapters/photocraft/target/debug/edit-session-photocraft-probe
```

The Rust adapters need Rust 1.99+ (tested with 1.99.1). For the bundled PhotoCraft adapter,
Cargo fetches both Rust repositories at fixed commits; no sibling checkout or path override is required.
See the [adapter README](adapters/photocraft/README.md). Each scenario starts a fresh process. Exit 0
means all scenarios passed and requested reports were written; 1 means a scenario or report
write failed; invalid CLI usage exits 2.

## Reports for CI

`--report FILE` writes JSON and `--junit FILE` writes JUnit XML; either or both are optional.
JUnit contains one test case per scenario, failure details and captured adapter stderr,
including failed assertions, invalid replies, nonzero exits and timeouts. The Python API
exposes these diagnostics as `CheckError.stderr`; JSON reports use `stderr`, and JUnit
uses `system-err`. Scenario failures keep their declared name and source path in both formats. If the
input cannot be parsed, its filename is used instead. A failed scenario does not prevent
the remaining scenarios from running or the reports from being written.

Each report is replaced atomically after a complete write. Create parent directories first.
Report paths that refer to a scenario input or to the other report (including existing
symlinks/hard links) are rejected before starting an adapter. Report write failures produce
a diagnostic on stderr and exit 1, even when every scenario passed. Characters forbidden by
XML 1.0 are replaced with U+FFFD in JUnit; the JSON report preserves the original strings.

## Scenario format

```json
{
  "schema": 1,
  "name": "Cancel a preview without changing history",
  "steps": [
    {"event": {"op": "begin"}, "expect": {"undo_depth": 0, "error": null}},
    {"event": {"op": "preview", "value": 0.5},
     "expect": {"committed": 1, "preview": 0.5, "undo_depth": 0, "error": null}},
    {"event": {"op": "cancel"},
     "expect": {"committed": 1, "preview": null, "undo_depth": 0, "error": null}}
  ]
}
```

Each request is a JSON line with `protocol: 1`, an integer `id`, and `event`.
The adapter returns exactly one JSON line per request with the same `protocol`/`id` and a
`state` object, then exits at stdin EOF. Logs go to stderr. Expectations are never sent to
the adapter. Objects match recursively by expected fields, including objects inside arrays.
Arrays must have the same length and order; each element uses the same matching rules.
Booleans are distinct from numbers. Missing fields are distinct from null.
Non-finite numbers, duplicate keys, missing/extra replies, wrong IDs, adapter crashes,
timeouts and malformed JSON fail the run.

JSONL records are separated by LF (CRLF also works), with an optional final newline.
Unicode line separators inside a JSON string are data, not record boundaries. Extra blank
lines are invalid. Inputs and replies allow at most 64 nested objects/arrays and must use
Unicode scalar values (no unpaired surrogates); malformed data fails with a diagnostic.

The whole scenario's events are sent in order. The adapter must process them sequentially
and finish each event before replying. This is semantic replay, not timed pointer playback.
Use a custom adapter to translate events into `egui_kittest` interactions or an app protocol.

## Existing tools and scope

Keep `egui_kittest` for widget/accessibility/pixel tests, `teatest` for Bubble Tea, and
`proptest` for input generation. This prototype adds a portable trace plus explicit assertions
and a machine-readable report; it does not replace those tools or discover bugs by itself.

The bundled engine-only PhotoCraft adapter drives real commands and history in a headless process. It does
not connect to the live application's UI or test its renderer, saved files or native input.
Upstream adoption is pending. The [PdfCraft adapter](adapters/pdfcraft/README.md) is owned
by the consumer repository and also uses engine save/reopen. The external [Bubbles](adapters/bubbles/README.md), [Huh](adapters/huh/README.md) and
[Cursive](adapters/cursive/README.md) adapters exercise their actual widget APIs.
Auto-recording and shrinking are not implemented.

Adapters are trusted local test programs, launched without a shell. A per-scenario timeout
defaults to five seconds. Input is limited to 1 MiB. Stdin and output capture use temporary
files so a non-reading adapter cannot block input delivery and logs do not grow in RAM.
While the adapter runs, stdout and stderr sizes are checked about every 50 ms; either
stream exceeding 1 MiB stops the adapter. A final check also catches fast-exiting writers.
At most 1 MiB of stderr is retained in a failure report.

Polling is not a hard disk quota: a fast writer can overshoot between checks. This is not
a sandbox. Timeout, output-limit handling and cancellation stop and reap the direct
adapter process, not a tree of spawned descendants. Adapters must manage their children.

## Evidence

- [PdfCraft UI report](reports/pdfcraft-properties.json): ten scenarios / 79 steps; see the
  [adapter instructions](adapters/pdfcraft/README.md) for immutable source pins and replay.

- [Alpha 2 review and regression checks](docs/VALIDATION.md): Unicode JSONL, report safety,
  JUnit, bounded JSON nesting and compatibility with existing PhotoCraft adapters.
- [Current PhotoCraft Session scenarios](photocraft-session-report.json): eight scenarios,
  41 steps, using the published Git dependency and real command dispatch. Each step also
  checks the command journal count, so previews and no-op commits cannot silently send edits.
- [Earlier PhotoCraft component scenarios](photocraft-report.json): eight scenarios against
  the original Document/History adapter, before switching to Session dispatch.
- [Earlier deliberate mutation](mutation-report.json): expected failures after disabling context
  protection in a temporary library copy. Stale-target and undo-back-to-original scenarios
  detect a wrong document mutation/history change. A third scenario detects the changed error.
- [Detailed validation](https://github.com/PerchAnton/edit-session/blob/main/docs/VALIDATION.md).

The same runner now passes real UI scenarios in both proposed consumers. The next milestone
is maintainer review of their behavior and dependency policy; this is not a claim of upstream adoption.

## JavaScript examples

[Ten external JavaScript adapters](adapters/javascript/README.md) replay editor history,
patches, store notifications and two-replica document operations against pinned stable
packages. These are optional development examples; upstream adoption is pending.

## License

Licensed under either the [MIT license](LICENSE-MIT) or the
[Apache License, Version 2.0](LICENSE-APACHE), at your option.
Unless explicitly stated otherwise, contributions submitted for inclusion are offered
under the same dual license.

## Additional external consumers

The third adapter batch adds ten native API examples. Textual and gocui deliberately test proposed fork fixes; upstream approval remains pending. See each adapter README for exact pins and coverage boundaries.

| Consumer | Scenarios / steps | Scope |
| --- | --- | --- |
| [prompt-toolkit](adapters/prompt-toolkit/README.md) | 3 / 21 | Native API observations; optional test tooling |
| [urwid](adapters/urwid/README.md) | 3 / 17 | Native API observations; optional test tooling |
| [asciimatics](adapters/asciimatics/README.md) | 3 / 15 | Native API observations; optional test tooling |
| [textual](adapters/textual/README.md) | 3 / 15 | Native API observations; optional test tooling |
| [reedline](adapters/reedline/README.md) | 3 / 17 | Native API observations; optional test tooling |
| [rustyline](adapters/rustyline/README.md) | 3 / 17 | Native API observations; optional test tooling |
| [rat-salsa](adapters/rat-salsa/README.md) | 3 / 18 | Native API observations; optional test tooling |
| [promptkit](adapters/promptkit/README.md) | 3 / 15 | Native API observations; optional test tooling |
| [tcell](adapters/tcell/README.md) | 3 / 13 | Native API observations; optional test tooling |
| [gocui](adapters/gocui/README.md) | 3 / 12 | Native API observations; optional test tooling |
