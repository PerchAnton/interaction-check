# From a replay failure to a native test

The useful deliverable can be a normal test in the consumer's own suite. Its CI does
not need to keep interaction-check. This guide uses the existing executable pyee and
XState examples; it does not generate code or claim that every replay exposes a new bug.

## 1. Save the checked prefix

From the repository root, with the XState example installed as described in its README:

```sh
python3 interaction_check.py --failure-dir failures --trace --report report.json \
  examples/xstate/scenarios/01-cancel.json -- node examples/xstate/adapter.mjs
```

On a state mismatch, `failures/0001.json` contains the original scenario metadata and
all steps through the first mismatch, including its original `expect`. File numbers
follow the input order, so names cannot collide. The report links to each saved file.
The directory must not exist; its parent must exist. A passing run leaves it empty.
Use a different output directory for the next run. `--trace` is optional for export.

Re-run a saved prefix before sharing it:

```sh
python3 interaction_check.py failures/0001.json -- node examples/xstate/adapter.mjs
```

The runner sends the entire event sequence before comparing responses. A batch adapter
can depend on later events; removing the tail is therefore **not a promise of equivalent
behavior**. The export is not a shortest/minimal test and does not automatically rerun
the adapter. Keep the adapter command, source revision and environment with your report.
Timeouts, crashes, malformed replies and input errors have no validated failing state:
they keep their diagnostic instead of exporting a guessed prefix. Review event data
before sharing it, as it can contain values from your own application.

## 2. Translate events and assertions into the project's own API

For [XState's cancel sequence](../examples/xstate/scenarios/01-cancel.json), `CHANGE` and
`CANCEL` map directly to `actor.send`. The native test uses a real actor, cleans it up,
and asserts the same saved/draft values:

```js
const actor = createActor(machine).start();
t.after(() => actor.stop());
actor.send({ type: "EDIT" });
actor.send({ type: "CHANGE", value: "preview" });
check(state(actor), { context: { draft: "preview", saved: "original" } });
actor.send({ type: "CANCEL" });
check(state(actor), { value: "idle", context: { saved: "original" } });
```

This excerpt comes from [the full native tests](../examples/xstate/native.test.mjs),
including imports and the `state` helper. `check` is Node's `partialDeepStrictEqual`;
it checks the same selected fields as the JSON expectations here. Those tests need
XState and Node, but neither Python nor the JSONL adapter:

```sh
cd examples/xstate
node --test native.test.mjs
```

For [pyee](../examples/pyee/test_once_reentrant.py), the behavior of interest lives
**inside** the callback: the once handler emits the same event again. Preserve that
ordering in the native test instead of replacing it with two top-level emits. The
complete pytest candidate asserts the callback order, remaining listeners and another
later emit. After setting up [the pinned audit environment](../examples/pyee/README.md),
run from the pyee source checkout so Python imports that exact source without installing it:

```sh
cd .artifacts/pyee-source
python -m pytest ../../examples/pyee/test_once_reentrant.py
```

Inspect existing tests first. The full pyee audit found one gap: 53 existing tests miss
one deliberately introduced remove-after-callback error; the candidate catches it.
Current pyee passes the candidate. Its maintainer has been offered the test, not a
new runner dependency. Details, raw results and limitations are in the pyee README.

## 3. Check that the assertion earns its place

Run the native test on correct code and on the smallest controlled change that violates
the intended behavior. It should pass the former and fail the latter for the expected
reason. If equivalent native coverage already exists, avoid adding a duplicate.

Keep replay when the reusable sequence and common report are useful across adapters.
Keep only the native regression when that is easier for the consumer to maintain.
Both outcomes are useful; neither establishes upstream adoption or general coverage.
