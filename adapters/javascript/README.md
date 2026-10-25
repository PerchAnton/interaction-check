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

Dependencies use exact published npm releases and a committed integrity-checked lockfile.
Install scripts are disabled. `versions.json` records registry metadata (including gitHead
where published); absent gitHead is unknown, not inferred from a repository's current main.
These examples do not claim to test unreleased main branches. Redux Observable uses the
upstream latest-tagged **3.0.0-rc.3 prerelease**, explicitly paired with Redux 5 and RxJS 7. Lexical packages resolve to
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
| [mobx](https://github.com/mobxjs/mobx) | 7.1.1 | 3 / 12 |
| [jotai](https://github.com/pmndrs/jotai) | 3.0.1 | 3 / 13 |
| [valtio](https://github.com/pmndrs/valtio) | 2.3.2 | 3 / 12 |
| [nanostores](https://github.com/nanostores/nanostores) | 1.5.5 | 3 / 13 |
| [effector](https://github.com/effector/effector) | 23.4.4 | 3 / 11 |
| [pinia](https://github.com/vuejs/pinia) | 4.1.0 (Vue 3.5.44) | 3 / 11 |
| [vue-reactivity](https://github.com/vuejs/core) | @vue/reactivity 3.5.44 | 3 / 13 |
| [rxjs](https://github.com/ReactiveX/rxjs) | 7.8.2 | 3 / 20 |
| [final-form](https://github.com/final-form/final-form) | 5.0.1 | 3 / 14 |
| [tanstack-store](https://github.com/TanStack/store) | @tanstack/store 0.11.2 | 3 / 14 |
| [zod](https://github.com/colinhacks/zod) | zod 4.6.7 | 3 / 9 |
| [valibot](https://github.com/open-circle/valibot) | valibot 1.5.0 | 3 / 9 |
| [yup](https://github.com/jquense/yup) | yup 1.7.1 | 3 / 9 |
| [ajv](https://github.com/ajv-validator/ajv) | ajv 8.20.0 | 3 / 9 |
| [joi](https://github.com/hapijs/joi) | joi 18.3.0 | 3 / 9 |
| [superstruct](https://github.com/ianstormtaylor/superstruct) | superstruct 2.0.2 | 3 / 9 |
| [arktype](https://github.com/arktypeio/arktype) | arktype 2.2.9 | 3 / 9 |
| [vest](https://github.com/ealush/vest) | vest 6.3.4 | 3 / 12 |
| [immutable-js](https://github.com/immutable-js/immutable-js) | immutable 5.1.9 | 3 / 11 |
| [reselect](https://github.com/reduxjs/reselect) | reselect 5.3.0 | 3 / 13 |
| [redux](https://github.com/reduxjs/redux) | redux 5.0.1 | 3 / 11 |
| [preact-signals](https://github.com/preactjs/signals) | @preact/signals-core 1.14.4 | 3 / 13 |
| [solid](https://github.com/solidjs/solid) | solid-js 1.9.17 | 3 / 13 |
| [svelte](https://github.com/sveltejs/svelte) | svelte 5.57.2 | 3 / 11 |
| [robot](https://github.com/matthewp/robot) | robot3 1.4.0 | 3 / 16 |
| [eventemitter3](https://github.com/primus/eventemitter3) | eventemitter3 5.0.4 | 3 / 11 |
| [formkit](https://github.com/formkit/formkit) | @formkit/core 2.1.2 | 3 / 13 |
| [redux-saga](https://github.com/redux-saga/redux-saga) | redux-saga 1.5.1 | 3 / 14 |
| [redux-observable](https://github.com/redux-observable/redux-observable) | redux-observable 3.0.0-rc.3 | 3 / 17 |
| [react-hook-form](https://github.com/react-hook-form/react-hook-form) | react-hook-form 7.91.0 | 3 / 14 |

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

### mobx

[Adapter](consumers/mobx.mjs) · [scenarios](../../scenarios/mobx)

Observable/computed reactions: action batching, equal writes and disposal. No React bindings or asynchronous flows.

### jotai

[Adapter](consumers/jotai.mjs) · [scenarios](../../scenarios/jotai)

Vanilla atoms in two stores: scope isolation, derived-value equality and unsubscribe. No React hooks, Suspense or async atoms.

### valtio

[Adapter](consumers/valtio.mjs) · [scenarios](../../scenarios/valtio)

Nested proxy writes, cached snapshots, retained immutable snapshots and synchronous subscriptions. No React or asynchronous notification batching.

### nanostores

[Adapter](consumers/nanostores.mjs) · [scenarios](../../scenarios/nanostores)

Native map/setKey and batch: final-state notifications, no-op writes and unsubscribe. No persistent stores, async tasks or framework bindings.

### effector

[Adapter](consumers/effector.mjs) · [scenarios](../../scenarios/effector)

Two native fork scopes, allSettled events, mapped stores, reset and SID-based serialization. No effects, SSR transport or framework bindings.

### pinia

[Adapter](consumers/pinia.mjs) · [scenarios](../../scenarios/pinia)

Two Pinia instances, object/function patches, reset and synchronous detached subscriptions. No component mounting, plugins or SSR hydration.

### vue-reactivity

[Adapter](consumers/vue-reactivity.mjs) · [scenarios](../../scenarios/vue-reactivity)

Conditional computed dependencies, equal derived values and effectScope disposal. No DOM, component rendering, compiler, Vapor or unreleased Vue APIs.

### rxjs

[Adapter](consumers/rxjs.mjs) · [scenarios](../../scenarios/rxjs)

Synchronous Subject/switchMap/distinctUntilChanged/takeUntil: stale inner emissions, cancellation and equality across switches. RxJS 7 only; not RxJS Next/9 compatibility. No timers or scheduler claims; keep native marble tests for timing.

### final-form

[Adapter](consumers/final-form.mjs) · [scenarios](../../scenarios/final-form)

Native createForm, registered field, synchronous validation/submission, reset versus restart and batched value notifications. No React, browser input, async validation or network submission.

### tanstack-store

[Adapter](consumers/tanstack-store.mjs) · [scenarios](../../scenarios/tanstack-store)

Native createStore derived dependencies, batch, equality and unsubscribe. Uses the current createStore API, not the older Derived class. No UI adapters or concurrent rendering.

### zod

[Adapter](consumers/zod.mjs) · [scenarios](../../scenarios/zod)

Native safeParse: trim/defaults, unknown-key stripping, strict numeric types and recovery after invalid input. No async refinements, JSON Schema conversion or AOT compilation.

### valibot

[Adapter](consumers/valibot.mjs) · [scenarios](../../scenarios/valibot)

Native safeParse/pipe: trim/defaults, unknown-key stripping, integer validation and error recovery. No async actions, Standard Schema integration or generated schemas.

### yup

[Adapter](consumers/yup.mjs) · [scenarios](../../scenarios/yup)

Native validateSync: cast versus strict mode, boolean conversion, defaults and multiple error paths. No async tests or React form bindings.

### ajv

[Adapter](consumers/ajv.mjs) · [scenarios](../../scenarios/ajv)

Compiled JSON Schema: explicit coercion, defaults, additional-property rejection and cleared errors between calls. The adapter clones the request before validation; the native working copy can change even when validation fails. No remote schemas or asynchronous keywords.

### joi

[Adapter](consumers/joi.mjs) · [scenarios](../../scenarios/joi)

Native object.validate: conversion on/off, trim/defaults, unknown-key stripping and collected error paths. No async external rules or HTTP framework integration.

### superstruct

[Adapter](consumers/superstruct.mjs) · [scenarios](../../scenarios/superstruct)

Native create/mask: unknown-key policy, coercion/defaults, explicit false values and accumulated failures. No TypeScript inference or custom async validation.

### arktype

[Adapter](consumers/arktype.mjs) · [scenarios](../../scenarios/arktype)

Native type invocation: undeclared-key deletion, optional fields, integer constraints and error recovery. No generated input schemas, async pipelines or compiler/performance claims.

### vest

[Adapter](consumers/vest.mjs) · [scenarios](../../scenarios/vest)

Stateful suite.run/only/get/reset: focused validation retains results for untouched fields and a full run revalidates them. No async races or framework bindings.

### immutable-js

[Adapter](consumers/immutable-js.mjs) · [scenarios](../../scenarios/immutable-js)

Native Map/List/setIn/withMutations: no-op identity, nested structural sharing and retained original snapshots. No adapter-defined undo history or performance claim.

### reselect

[Adapter](consumers/reselect.mjs) · [scenarios](../../scenarios/reselect)

Native createSelector/lruMemoize: unrelated state updates, resultEqualityCheck reference reuse and filter ordering. The state fixture is original; no React or devtools coverage.

### redux

[Adapter](consumers/redux.mjs) · [scenarios](../../scenarios/redux)

Core legacy_createStore/combineReducers/applyMiddleware: notifications on no-op dispatch, middleware order, unsubscribe and replaceReducer state retention. A core API reproduction, not a recommendation to replace Redux Toolkit in apps.

### preact-signals

[Adapter](consumers/preact-signals.mjs) · [scenarios](../../scenarios/preact-signals)

Native signals/computed/effect/batch: dynamic dependencies, final-state batch notification and observer disposal. No Preact rendering or DOM.

### solid

[Adapter](consumers/solid.mjs) · [scenarios](../../scenarios/solid)

Published solid-js/dist/solid.js client reactive runtime selected explicitly because Node defaults to SSR. createRoot/createComputed/createMemo/batch: dependency switching, batching and disposal. No JSX, DOM, SSR or browser behavior claims.

### svelte

[Adapter](consumers/svelte.mjs) · [scenarios](../../scenarios/svelte)

Native svelte/store writable/derived/get: same-object writes notify, derived reads after unsubscribe and independent fields. No compiler, runes, components or DOM.

### robot

[Adapter](consumers/robot.mjs) · [scenarios](../../scenarios/robot)

Original synchronous draft machine interpreted by robot3: edit/cancel, validation guard and out-of-state events. No arbitrary-machine correctness, async invoke or browser bindings.

### eventemitter3

[Adapter](consumers/eventemitter3.mjs) · [scenarios](../../scenarios/eventemitter3)

Native EventEmitter: context binding, once removal before reentrant emission, removeListener and listener-free emit. No performance or compatibility claims for other emitter implementations.

### formkit

[Adapter](consumers/formkit.mjs) · [scenarios](../../scenarios/formkit)

Native core node tree: child input propagation, tree reset and blocking-message ledger accounting. input(value,false) is explicit; settlement is awaited. No Vue/React rendering or validation plugin.

### redux-saga

[Adapter](consumers/redux-saga.mjs) · [scenarios](../../scenarios/redux-saga)

Native runSaga/stdChannel/takeLatest: obsolete worker cancellation, ignored stale resolution and root cancellation. Responses are explicit channel events; no wall-clock timer or network.

### redux-observable

[Adapter](consumers/redux-observable.mjs) · [scenarios](../../scenarios/redux-observable)

Published latest-tagged 3.0.0-rc.3 prerelease with Redux 5 and RxJS 7: real epic middleware, switchMap, inner cancellation and root stop. No timers, UI or stable-release compatibility claim.

### react-hook-form

[Adapter](consumers/react-hook-form.mjs) · [scenarios](../../scenarios/react-hook-form)

Native createFormControl: required/minLength validation, dirty/touched reset and valid/invalid submit callbacks. Validation/submission are awaited. No React mounting, DOM events, async resolver or network.

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

The reactive examples run synchronously except for explicitly awaited Effector allSettled.
Expected states and notification sequences are hand-authored before execution. Five input
regressions verify that an invalid final batch argument leaves both native values and
notification history unchanged. There are no real-time sleeps or network effects.

Validation traces expose native results, output keys, sorted error paths and request-input
equality. They do not compare translated error messages or treat these libraries as
interchangeable. Ajv deliberately validates a working copy: default/coercion writes can
survive a failed validation on that copy. The Robot machine, Redux reducer and saga/epic
are small original consumer fixtures. Their state transitions remain owned by native APIs.
