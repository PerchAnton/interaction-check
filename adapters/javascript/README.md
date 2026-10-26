# JavaScript consumer adapters

Experimental external examples maintained by PerchAnton. These adapters call the actual
published libraries; no copied upstream source or substitute editor/state model is bundled.
They add no runtime dependency to those projects. Upstream adoption is pending.

## Reproduce

Use Node.js 24.19.0 and Python 3.10+. From the repository root:

```sh
npm --prefix adapters/javascript ci --ignore-scripts --no-audit --no-fund
npm --prefix adapters/javascript test
npm --prefix adapters/javascript run format:check
python adapters/javascript/replay.py --reports /path/to/temporary/reports
```

Or replay one consumer (the example uses POSIX shell expansion):

```sh
python interaction_check.py scenarios/slate/*.json -- node adapters/javascript/main.mjs slate
```

The Python launcher expands paths itself on Windows, Linux and macOS. Every scenario
starts a fresh Node process. Only event objects reach the adapter; assertions stay in the
runner. A failed API call or invalid operation fails the process with a diagnostic.
The JSONL transport limits records/replies to 64 KiB and events to 1024. Text event fields
are limited to 4096 valid UTF-16 units; offsets must be safe non-negative integers in range.
The runner applies its own input, nesting, process-time and output limits.

Dependencies use exact stable npm releases and a committed integrity-checked lockfile.
Install scripts are disabled. `versions.json` records registry metadata (including gitHead
where published); absent gitHead is unknown, not inferred from a repository's current main.
These examples do not claim to test unreleased main branches. Lexical packages resolve to
one matching version. Tiptap/Quill use jsdom rather than a browser. Keep native project
unit tests, property-based tests and Playwright for coverage outside the table below.

## Consumers and boundaries

| Consumer | Tested stable versions | Scenarios / steps |
| --- | --- | --- |
| [slate](https://github.com/ianstormtaylor/slate) | slate 0.146.0, slate-history 0.144.0 | 3 / 17 |
| [lexical](https://github.com/facebook/lexical) | lexical 0.52.0, @lexical/headless 0.52.0, @lexical/history 0.52.0 | 3 / 16 |
| [tiptap](https://github.com/ueberdosis/tiptap) | @tiptap/core 3.32.0, @tiptap/starter-kit 3.32.0 | 3 / 16 |
| [quill](https://github.com/slab/quill) | quill 2.0.3 | 3 / 14 |
| [immer](https://github.com/immerjs/immer) | immer 11.2.9 | 3 / 12 |
| [zustand](https://github.com/pmndrs/zustand) | zustand 5.0.16 | 3 / 13 |
| [xstate](https://github.com/statelyai/xstate) | xstate 5.33.3 | 3 / 18 |
| [yjs](https://github.com/yjs/yjs) | yjs 13.6.33 | 3 / 17 |
| [automerge](https://github.com/automerge/automerge) | @automerge/automerge 3.5.0 | 3 / 15 |
| [redux-toolkit](https://github.com/reduxjs/redux-toolkit) | @reduxjs/toolkit 2.13.0 | 3 / 13 |

### slate

[Adapter](consumers/slate.mjs) · [scenarios](../../scenarios/slate)

Native Transforms, selected Unicode replacement, empty deletion and redo invalidation. No slate-react, keyboard, IME or browser selection coverage.

### lexical

[Adapter](consumers/lexical.mjs) · [scenarios](../../scenarios/lexical)

Headless editor updates, explicit history entries, immutable saved EditorState and JSON round trips. No DOM, React, nested editor or IME coverage.

### tiptap

[Adapter](consumers/tiptap.mjs) · [scenarios](../../scenarios/tiptap)

Mounted Editor with StarterKit in jsdom; selected replacement, bold, undo/redo and literal angle brackets. Mounting is necessary to install history plugins. No real-browser focus, layout or key-event coverage.

### quill

[Adapter](consumers/quill.mjs) · [scenarios](../../scenarios/quill)

Real Quill in jsdom: Delta content, Unicode deletion, formatting and History. scrollSelectionIntoView is disabled because jsdom has no layout; scrolling, browser input and clipboard are untested.

### immer

[Adapter](consumers/immer.mjs) · [scenarios](../../scenarios/immer)

produceWithPatches/applyPatches, inverse array patches, no-op identity and structural sharing. The adapter retains the latest patch pair; it is not an undo stack or a concurrency/rebase implementation.

### zustand

[Adapter](consumers/zustand.mjs) · [scenarios](../../scenarios/zustand)

Vanilla createStore and subscribeWithSelector: no-op/irrelevant updates, unsubscribe, replacement and initial-state isolation. No React bindings, persist middleware or browser storage.

### xstate

[Adapter](consumers/xstate.mjs) · [scenarios](../../scenarios/xstate)

A contributor-original synchronous draft machine runs on createActor: cancel, validation guard, persisted snapshot and restore. Tests the supplied example machine, not arbitrary machines, timers, async actors or v6 APIs.

### yjs

[Adapter](consumers/yjs.mjs) · [scenarios](../../scenarios/yjs)

Two real Y.Doc text replicas, encoded updates, duplicate delivery and origin-scoped UndoManager. Explicit undo groups, remote changes retained. No network provider, awareness, rich-text bindings or v14 APIs.

### automerge

[Adapter](consumers/automerge.mjs) · [scenarios](../../scenarios/automerge)

Two native documents, concurrent text splices, merge idempotence, binary save/load and historical views. Uses deterministic initial actor IDs; no network sync protocol, fuzzing or conflict explorer.

### redux-toolkit

[Adapter](consumers/redux-toolkit.mjs) · [scenarios](../../scenarios/redux-toolkit)

Native sorted createEntityAdapter reducers inside configureStore: duplicate IDs, missing updates/removals, reordering and immutable initial state. No React bindings, RTK Query or async middleware.

## Design choices

History grouping is explicit: Slate withNewBatch, Lexical HISTORY_PUSH_TAG, Tiptap
closeHistory, Quill delay=0 and Yjs captureTimeout=0. This removes wall-clock dependence;
it does not test native time-based typing coalescence. Collaborative traces edit distinct
positions so expectations do not rely on randomly generated client IDs.

The XState machine and Redux slice are small original example applications. Their scenario
expectations were written before execution. Native histories, patch generation, reducers,
notifications, persistence and CRDT merges remain owned by the respective libraries.

The Rust edit-session library is not injected through an FFI/WASM wrapper: these examples
already have native snapshots, transactions or draft handling, and no benefit from that
additional runtime boundary has been demonstrated.
