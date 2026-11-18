# Real library traces across a consumer boundary

These examples call installed **Mutative 2.0.2**, **zundo 2.3.0 / Zustand 5.1.0**,
**EventEmitter2 6.4.9**, and **Python jsonpatch 1.39**. They do not replace native
tests or claim accepted upstream integrations. All workarounds live in these
application adapters; the runner and dependency sources are unchanged.

## Run

From the repository root, with Python 3.10+ and Node 24+:

```sh
python3 -m venv .venv-interop
.venv-interop/bin/python -m pip install -r examples/interop/requirements.txt
npm --prefix examples/interop ci --ignore-scripts --no-audit --no-fund
node --test examples/interop/*.test.mjs
.venv-interop/bin/python examples/interop/verify.py --report artifacts/interop/evidence.json
```

On Windows use `.venv-interop\Scripts\python.exe`. React is pinned because the
published zundo entry imports Zustand's React entry, even though this example
only uses vanilla stores. These dependencies belong to the example, not the
zero-runtime-dependency Python runner.

The verifier requires all adapted traces to pass, compares full Python/Mutative
observations, and requires three raw dependency failures at precise steps. An
import failure or process crash does not count as detecting a regression.
It writes JSON evidence and expected/observed event tables with Mermaid diagrams.

## Python producer → Mutative consumer

[Mutative #127](https://github.com/unadlib/mutative/issues/127) describes receiving
Python JSON Patch operations. The maintainer recommends a converter because
Mutative's `apply` is intended for its own add/remove/replace patches.

```sh
.venv-interop/bin/python examples/interop/producer.py > artifacts/produced.json
.venv-interop/bin/python interaction_check.py --trace --report artifacts/patch-report.json \
  artifacts/produced.json -- node examples/interop/main.mjs patch
```

Create `artifacts` first if it does not exist. `producer.py` uses real
`JsonPatch.from_diff`; expected output is the producer's independently specified
desired document. The same checked-in scenarios also run against real
`JsonPatch.apply(in_place=False)`. Expectations never reach either adapter.

The bridge supports non-root JSON pointers and add/remove/replace/move/copy on
JSON object documents. It resolves a move's destination after removal and clones
copied values. A failed batch leaves the published document unchanged; intermediate
immutable values stay local. It rejects root operations, `test`, reserved prototype
paths and noncanonical array indices. It is not a complete RFC 6902 implementation,
a security boundary for arbitrary untrusted documents, or in-place patch semantics.

Without the bridge, `patch-move.json` fails at step 2: the document did not move.
With the bridge, all patch scenarios and the Python-generated patch agree. Native
tests remain the simpler choice for a single JavaScript implementation; the extra
runner is useful here because the trace crosses Python and JavaScript.

## Undo / Redo boundaries

[zundo #220](https://github.com/charkour/zundo/issues/220) already has
[PR #221](https://github.com/charkour/zundo/pull/221). This is not a second fix PR.
The native test reproduces `undo(0)` replacing the store with `undefined`.

The example's **application policy** treats nonpositive, noninteger and nonnumeric
counts as no-ops. This is not a claim about the eventual upstream API policy.
Positive counts use the real middleware, including its boundary behavior. The
adapter observes value presence separately from `null`, both history stacks,
callbacks for this step, and the accumulated subscription log.

```sh
python3 interaction_check.py --trace --report artifacts/history.json \
  examples/interop/scenarios/history-invalid.json -- node examples/interop/main.mjs history
```

Use `history-raw` to see the unguarded step-3 mismatch. The report is a portable
reproduction, not proof that adding Python is worthwhile for a few assertions.

## Event writes, callbacks and logs

[EventEmitter2 #316](https://github.com/EventEmitter2/EventEmitter2/issues/316)
already has [PR #323](https://github.com/EventEmitter2/EventEmitter2/pull/323).
With wildcard enabled and newListener disabled, the raw string and single-element
array forms behave differently. The narrow workaround maps only `["newListener"]`
to the existing string route; it does not reinterpret other array namespaces.

```sh
python3 interaction_check.py --trace --report artifacts/events.json \
  examples/interop/scenarios/events-log.json -- node examples/interop/main.mjs events
python3 examples/interop/render.py artifacts/events.json > artifacts/events.md
```

`write` changes application state but emits nothing. `emit` calls the real emitter.
`callbacks` contains only the current step; `log` accumulates all delivered
callbacks. The renderer requires all three observations and draws only checked
steps. A matching final value cannot hide a duplicate callback. With `events-raw`,
the name-comparison trace fails at step 5 and the diagram shows the unexpected
callback. No readability advantage has yet been measured with a new developer.

## Limits and maintenance cost

The protocol adapter receives a whole batch, so later events may have run even
when a report stops at the first checked mismatch. Rerun an exported prefix before
calling it a reproduction; it is not automatically a minimal test case. These
adapters do not inspect rendering, physical input or asynchronous callback races.
Private field values are included in ordinary trace reports: review before sharing.
Dependency locks, adapter contracts and native tests all need maintenance. Keep
the native test alone when a portable cross-version trace does not repay that cost.
