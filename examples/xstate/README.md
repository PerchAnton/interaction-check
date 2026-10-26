# A small XState reproduction you can review

This example answers [feedback on the external adapter](https://github.com/statelyai/xstate/discussions/5824#discussioncomment-19181718):
show the trace format and the state after each event. It runs an original synchronous
draft machine on **XState 5.33.3**. It is not a reported XState defect or an accepted
upstream integration. Keep XState's [native testing tools](https://stately.ai/docs/testing).

## Run from the repository root

Requires Python 3.10+ and Node 24.15+. Only XState is installed; no other example's
dependencies, test framework package or install scripts are needed.

```sh
npm --prefix examples/xstate ci --ignore-scripts --no-audit --no-fund
node --test examples/xstate/native.test.mjs examples/xstate/adapter.test.mjs
python3 examples/xstate/verify.py --report xstate-evidence.json
```

The last command replays **3 scenarios / 18 steps**, checks three deliberate mutations
in temporary copies, and writes states and failure evidence. The three printed `FAIL`
lines are expected mutation checks; exit 0 means the verification itself succeeded.
Paths are expanded in Python, so the command also works on Windows (`python` if needed).

To replay just one trace, with a report suitable for attaching to a bug report:

```sh
python3 interaction_check.py --trace --report xstate-validation.json \
  examples/xstate/scenarios/02-validation.json -- node examples/xstate/main.mjs
```

## Events and observations

A scenario is a JSON object with `schema: 1`, a `name` and ordered `steps`.
Each step contains exactly `event` and a nonempty `expect` object:

```json
{"event": {"op": "send", "type": "CHANGE", "value": " "}, "expect": {"can_save": false}}
```

| Event | Meaning |
| --- | --- |
| `{"op":"new"}` | Start an actor from the initial machine state; clear the checkpoint. |
| `{"op":"send","type":"EDIT"}` | Begin editing the saved value. |
| `{"op":"send","type":"CHANGE","value":"text"}` | Send a text proposal while editing. |
| `{"op":"send","type":"CANCEL"}` | Return to idle without updating saved text. |
| `{"op":"send","type":"SAVE"}` | Save only if the draft is not blank. |
| `{"op":"checkpoint"}` | JSON-round-trip the actor's persisted snapshot. |
| `{"op":"restore"}` | Stop the actor and create one from that checkpoint. |

`new` must precede the other operations, and `checkpoint` must precede `restore`.
Unsupported operations and malformed input fail the adapter. An event that the
machine does not handle in its current state has XState's native behavior.
The adapter observes `value`, `context`, `status`, and `can_save` using `getSnapshot()`
and `snapshot.can({type: "SAVE"})`. The runner receives that state, then checks `expect`.

**Expectations never reach the adapter.** Objects match by the requested fields, even
inside arrays. Arrays have exact length/order; `false` differs from `0`, and a missing
key differs from `null`. Omitted fields are not assertions. See the full
[protocol contract](../../README.md#scenario-format).

## State after every step

These are full observed summaries. The checked-in traces assert selected fields; the
tables do not silently add assertions to them. `status` is `active` throughout.

### Cancel and begin another edit

| Step | Event | value | saved | draft | can_save |
| --- | --- | --- | --- | --- | --- |
| 1 | new | idle | original | original | false |
| 2 | EDIT | editing | original | original | true |
| 3 | CHANGE("preview") | editing | original | preview | true |
| 4 | CANCEL | idle | original | preview | false |
| 5 | EDIT | editing | original | original | true |

CANCEL leaves the saved value unchanged. This machine resets the draft on the next EDIT.

### Reject blank input, then correct it

| Step | Event | value | saved | draft | can_save |
| --- | --- | --- | --- | --- | --- |
| 1 | new | idle | original | original | false |
| 2 | EDIT | editing | original | original | true |
| 3 | CHANGE(" ") | editing | original | one space | false |
| 4 | SAVE | editing | original | one space | false |
| 5 | CHANGE("界🙂") | editing | original | 界🙂 | true |
| 6 | SAVE | idle | 界🙂 | 界🙂 | false |

### Restore a checkpoint

| Step | Event | value | saved | draft | can_save |
| --- | --- | --- | --- | --- | --- |
| 1 | new | idle | original | original | false |
| 2 | EDIT | editing | original | original | true |
| 3 | CHANGE("saved draft") | editing | original | saved draft | true |
| 4 | checkpoint | editing | original | saved draft | true |
| 5 | CHANGE("later") | editing | original | later | true |
| 6 | restore | editing | original | saved draft | true |
| 7 | SAVE | idle | saved draft | saved draft | false |

## What an actionable failure looks like

The verifier deliberately replaces the example's nonblank guard with `() => true`.
It must fail at validation step 3 with `state.can_save: expected False, got True`.
The report retains steps 1 and 2 plus this failed entry:

```json
{
  "step": 3,
  "event": {"op": "send", "type": "CHANGE", "value": " "},
  "expect": {"can_save": false},
  "actual": {
    "value": "editing",
    "context": {"saved": "original", "draft": " "},
    "status": "active",
    "can_save": true
  },
  "passed": false,
  "differences": ["state.can_save: expected False, got True"]
}
```

Only checked steps are recorded. The adapter has already received the whole sequence;
unrecorded later events may have executed. A bad envelope has no invented actual state.
A process crash/timeout is reported as a process error, not a valid snapshot sequence.
Trace reports contain event and state data: select appropriate fields before sharing.

## Use in a real bug report

Start with the scenario, pinned dependency version, command, full failure report and
the relevant machine. Change `machine.mjs` to the smallest real application machine
that reproduces the issue; adapt the event/snapshot mapping if its API differs. Keep
assertions in the scenario. The example is not an adapter for arbitrary machines.

There is no timer, promise, invoked actor, browser, network or model-based exploration
coverage. The saved snapshot stays in memory; no persisted-file migration is tested.
The runner is a trusted local tool, not a sandbox for downloaded adapters.

## Is it worth using?

[Measured comparison](../../docs/VALUE.md) includes the ordinary native tests, the
adapter and transport cost, raw timings, reproducible commands and limitations.
Native tests are shorter and faster in this pilot. Choose traces when a separate
reviewable artifact and common CI report are useful, not to improve execution speed.
