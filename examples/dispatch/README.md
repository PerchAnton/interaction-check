# From JSON to real property callbacks

This example calls **python-dispatch 0.2.3**, not a simulation. It is external
evaluation code maintained here, not an upstream integration or a discovered bug.
From current source (these files are newer than the alpha.7 tag), in a virtual environment:

```sh
python -m pip install -r examples/dispatch/requirements.txt
python examples/dispatch/verify.py --check
```

The command runs 3 ordinary tests, 5 replay steps, and a deliberately incorrect
expectation that must fail at step 2. The extra package is for this example only;
the runner still has no runtime dependencies.

| Term | Meaning |
| --- | --- |
| Write | Assignment to `model.count`; an equal assignment may emit nothing |
| Callback | One invocation of the retained receiver |
| New callbacks | The suffix added to `log` during this step |
| `log` | All callback values since the adapter started, in order |
| `count` | Current **property value**, not the number of callbacks |

The [complete trace](trace.md) has separate expected/observed tables and Mermaid
diagrams. At step 2, three locked writes `[2, 3, 4]` produce one new callback `[4]`;
the cumulative log is `[1, 4]`. After unbinding, writing `5` changes `count` but leaves
the log unchanged. See the library's [property API](https://python-dispatch.readthedocs.io/en/latest/properties.html).

## JSON → adapter → actual API → comparison

```json
{"event": {"op": "write", "values": [2, 3, 4], "locked": true},
 "expect": {"count": 4, "log": [1, 4]}}
```

1. The runner sends only `event`, a protocol number and a step ID to [adapter.py](adapter.py).
2. The adapter opens `model.emission_lock("count")` and assigns each value to a real `Property`.
3. The receiver appends observed notifications. The adapter returns `count` and `log`.
4. The runner compares that snapshot with `expect`, which the adapter never receives.

The verifier separately changes **only the expected log** at step 2 to `[1, 2, 3, 4]`.
The real library returns `[1, 4]`, and the runner reports the first mismatch.
[View both sides](mismatch.md). This is a mistaken expectation, not an upstream defect.
All five actions may execute before the two-step checked prefix is reported. A diagram
summarizes steps; it does not infer callback timing within a step.

## Optional diagrams for another run

```sh
python interaction_check.py --trace --report dispatch-report.json examples/dispatch/scenario.json -- python examples/dispatch/adapter.py
python examples/dispatch/render.py dispatch-report.json > dispatch-trace.md
```

The renderer lives in this source example, not the installed runner. It requires
complete integer `count`/append-only `log` snapshots and rejects incompatible or partial
states instead of inventing events. Compact reports must be rerun with `--trace`.
Only checked steps are drawn; Markdown tables work without Mermaid.

Run the verifier without `--check` to regenerate [evidence](../../docs/evidence/dispatch.json)
and diagrams. CI reruns the real library and checks source hashes. These are behavior
checks, not coverage or speed measurements.

## A native test may be enough

[native_tests.py](native_tests.py) uses `Dispatcher`, `Property` and `unittest` directly:

```sh
python -m unittest discover -s examples/dispatch -p native_tests.py -v
```

Use that route for one regression. Replay earns its extra files only when sharing
the actions and observations is useful. This example does not cover async delivery,
multiple-listener ordering, rendering, focus, clipboard or application side effects.
[The same explanation for rat-salsa](../../docs/REAL_API_WALKTHROUGH.md).
