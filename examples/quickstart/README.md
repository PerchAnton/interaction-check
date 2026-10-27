# Understand the runner with one small editor

This original teaching model edits a title in memory. It does not open a GUI, write a
file, use edit-session, or reproduce a third-party bug. Python 3.10+ is enough; there
are no packages to install for this example.

## One command, including a deliberate failure

From the repository root:

```sh
python examples/quickstart/verify.py
```

The script runs three native tests and three JSON scenarios (12 steps). It then changes
**a temporary copy** of `editor.py` so Cancel incorrectly saves the draft. Both methods
must detect that defect. The printed `FAIL` is expected; exit 0 means the complete
verification succeeded. Your checkout stays unchanged. The verifier also exports the
failing prefix, checks that its original expectations survive, and reruns it.

The observable failure is:

```text
FAIL Cancel keeps the saved title
  Step 3 ({'op': 'cancel'}): state.saved: expected 'Original', got 'Preview'
```

## Follow the data

| File | Responsibility |
| --- | --- |
| [editor.py](editor.py) | The example's behavior: open, type, save and cancel |
| [01-cancel.json](scenarios/01-cancel.json) | Actions and expected values, written by the test author |
| [adapter.py](adapter.py) | Calls `Editor` methods and returns observed values |
| [interaction_check.py](../../interaction_check.py) | Starts the adapter and compares those values with expectations |
| [native_tests.py](native_tests.py) | Checks the same three behaviors directly with `unittest` |

For example, one scenario step says:

```json
{"event": {"op": "cancel"}, "expect": {"saved": "Original", "draft": null}}
```

Only `event` reaches the adapter; `expect` stays in the runner. On correct code Cancel
discards the draft. In the deliberate broken copy, the returned `saved` field is
`Preview`, so the comparison fails. The runner is not recording clicks or generating
expectations, and this adapter is a small teaching fixture, not a generic editor API.

Run the correct Cancel case by itself:

```sh
python interaction_check.py --trace --report quickstart-report.json examples/quickstart/scenarios/01-cancel.json -- python examples/quickstart/adapter.py
```

This command passes. The automated verifier introduces the defect in a temporary
directory; there is no hidden broken mode in the checked-in application model.

## Compare with a normal test

```sh
python -m unittest discover -s examples/quickstart -p native_tests.py -v
```

A native test can simply open the draft, type `Preview`, cancel, and assert that the
saved title is still `Original`. It needs neither the adapter nor interaction-check.

| Run | Native tests | Replay scenarios |
| --- | --- | --- |
| Correct teaching model | 3 pass | 3 pass / 12 steps |
| Cancel incorrectly saves | 2 pass, 1 assertion fails | 2 pass, 1 state mismatch |

These are different test units, not a coverage percentage or speed benchmark. Both
detect the same one selected defect. For this small example, the native test is the
simpler choice. Replay is an option when sharing the JSON case and its observed states
is useful enough to maintain an adapter. [Choosing the tool](../../docs/CHOOSING.md).

## Export is a checked prefix, not a stopped execution

The Cancel scenario has **4 actions**. The broken adapter processes all four, but
comparison stops at step **3**, producing a three-step checked prefix. The verifier
explicitly checks both facts. Later actions may already have had effects: the tool
does not stop the application at the first incorrect state.

This prefix reruns with the same mismatch in this example. Other adapters may depend
on later actions, so always rerun an export before sharing it. Export does not minimize
the case or create a native test automatically. [Native-test handoff](../../docs/NATIVE_TESTS.md).

## Reproduce the evidence

```sh
python examples/quickstart/verify.py --report docs/evidence/quickstart.json
python tools/render_quickstart.py
python tools/render_quickstart.py --check
```

The [saved JSON](../../docs/evidence/quickstart.json) contains outcomes, the actual
mismatch and LF-normalized source hashes. The [README diagram](../../docs/assets/quickstart.svg)
is generated from that JSON. CI reruns the experiment and checks the diagram's source
hashes on Linux, macOS and Windows. This is separate from the 49 runner tests and the
older XState/pyee measurements; those counts are not silently combined.

To verify with a package already installed in a virtual environment, run that
environment's Python with `examples/quickstart/verify.py --installed`. The example
files belong to the source checkout; the wheel contains the runner. The walkthrough
uses protocol 1 and works with the published `0.1.0a7` package. It was also verified
with the earlier `0.1.0a6` package; the runner behavior is unchanged.
