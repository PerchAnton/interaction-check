# interaction-check

**Experimental, 0.1.0-alpha.1.** An independent development tool for replaying semantic
interaction traces against an explicit local adapter. No third-party Python packages.
Maintained by [PerchAnton](https://github.com/PerchAnton); no PyPI release or upstream adoption.

The first adapter uses the independent [edit-session library](https://github.com/PerchAnton/edit-session)
from a fixed Git revision, and commits through PhotoCraft's actual `Session` command API.
The tool itself
knows nothing about opacity, PDF geometry, Rust, Go or a GUI framework. A future PdfCraft
adapter would translate scenarios to that application's existing command and inspection APIs.

## Run

Requires Python 3.10+ (tested with Python 3.14 on macOS arm64).

```sh
python3 -m unittest -v
cargo build --locked --manifest-path adapters/photocraft/Cargo.toml
python3 interaction_check.py --report result.json scenarios/photocraft/*.json -- \
  adapters/photocraft/target/debug/edit-session-photocraft-probe
```

Only the PhotoCraft adapter needs Rust (1.99+; tested with 1.99.1). Cargo fetches both Rust
repositories at fixed commits; no sibling checkout or path override is required.
See the [adapter README](adapters/photocraft/README.md). Each scenario starts a fresh process. Exit 0
means all scenarios passed; 1 means at least one failed; invalid CLI usage exits 2.

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
the adapter. Objects match recursively by expected fields; arrays match in full and in
order; booleans are distinct from numbers. Missing fields are distinct from null.
Non-finite numbers, duplicate keys, missing/extra replies, wrong IDs, adapter crashes,
timeouts and malformed JSON fail the run.

The whole scenario's events are sent in order. The adapter must process them sequentially
and finish each event before replying. This is semantic replay, not timed pointer playback.
Use a custom adapter to translate events into `egui_kittest` interactions or an app protocol.

## Existing tools and scope

Keep `egui_kittest` for widget/accessibility/pixel tests, `teatest` for Bubble Tea, and
`proptest` for input generation. This prototype adds a portable trace plus explicit assertions
and a machine-readable report; it does not replace those tools or discover bugs by itself.

The PhotoCraft adapter drives real engine commands and history in a headless process. It does
not connect to the live application's UI or test its renderer, saved files or native input.
Upstream PhotoCraft has not adopted these dependencies. No PdfCraft or Bubbles adapter is
implemented. There is no auto-recording or shrinking yet.

Adapters are trusted local test programs, launched without a shell. A per-scenario timeout
defaults to five seconds. Input and captured output are limited to 1 MiB; output limits are
checked after execution, with file-backed capture. This is not a sandbox or a CPU/disk quota.
The current timeout controls the direct adapter process, not a tree of spawned descendants.

## Evidence

- [Current PhotoCraft Session scenarios](photocraft-session-report.json): eight scenarios,
  41 steps, using the published Git dependency and real command dispatch. Each step also
  checks the command journal count, so previews and no-op commits cannot silently send edits.
- [Earlier PhotoCraft component scenarios](photocraft-report.json): eight scenarios against
  the original Document/History adapter, before switching to Session dispatch.
- [Earlier deliberate mutation](mutation-report.json): expected failures after disabling context
  protection in a temporary library copy. Stale-target and undo-back-to-original scenarios
  detect a wrong document mutation/history change. A third scenario detects the changed error.
- [Detailed validation](https://github.com/PerchAnton/edit-session/blob/main/docs/VALIDATION.md).

The next adoption milestone is one real UI trace for PhotoCraft and one for PdfCraft,
using existing harnesses. Cross-application reuse is still a hypothesis until both work.

## License

Licensed under either the [MIT license](LICENSE-MIT) or the
[Apache License, Version 2.0](LICENSE-APACHE), at your option.
Unless explicitly stated otherwise, contributions submitted for inclusion are offered
under the same dual license.
