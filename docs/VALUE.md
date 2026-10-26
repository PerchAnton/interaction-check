# Measured value and adoption limits

26 October 2026. This is a focused response to [XState discussion feedback](https://github.com/statelyai/xstate/discussions/5824#discussioncomment-19181718),
not a claim that a large adapter catalogue demonstrates adoption. The useful deliverable
is an executable event sequence with expected and observed state after each checked step.

## A smaller installation for one example

The [focused XState walkthrough](../examples/xstate/README.md) installs only XState.
The previous ten-consumer bundle remains available in its separate adapter proposal.

| Measure | Previous JavaScript bundle | Focused XState example |
| --- | ---: | ---: |
| Non-root package entries in lockfile | 120 | 1 |
| Lockfile bytes | 58,445 | 735 |
| XState version | 5.33.3 | 5.33.3 |
| XState scenarios / checked steps | 3 / 18 | 3 / 18 |

This removes **119 of 120 package entries (99.2%) from the installation needed for
this example** by excluding the other consumers and formatter. It does not shrink
XState itself, improve its speed or compare dependency counts against a native test:
a native test also needs only XState. Package entries count dependencies including
development dependencies, not bytes installed, download requests or vulnerabilities.

Baseline: [lockfile at ae3bcefb](https://github.com/PerchAnton/interaction-check/blob/ae3bcefbf4a82d9e1baadecd2feec948f96a9195/adapters/javascript/package-lock.json).
The [baseline metadata](evidence/xstate-install-baseline.json) records its SHA-256 and
exact size. Recount any saved lockfile with:

```sh
python3 -c 'import json,pathlib,sys; p=pathlib.Path(sys.argv[1]); print(len(json.loads(p.read_text())["packages"])-1, p.stat().st_size)' package-lock.json
```

## Native assertions remain a strong alternative

Both implementations use the same original `machine.mjs` and check the same 18 states.
[Native tests](../examples/xstate/native.test.mjs) call the actor directly using Node's
built-in assertions. The trace path sends events to an external adapter and compares
selected fields in Python. Neither implementation uses timing-sensitive state changes.

| Checked-in source | Physical lines | UTF-8 bytes |
| --- | ---: | ---: |
| Shared example machine | 28 | 695 |
| Native tests, including snapshot projection | 60 | 2,662 |
| Three JSON scenarios | 36 | 1,947 |
| Replay adapter + entry point + bounded JSONL transport | 158 | 4,339 |
| Generic Python runner, reused across consumers | 334 | 15,630 |

Counts include blank lines/comments and depend on formatting. JSON's 36 lines are
**not** a code-reduction claim: the adapter, transport and runner also cost maintenance.
Lockfiles, verification tooling, boundary tests and documentation are additional files,
excluded from both executable-source comparisons above. File hashes and individual
counts are in [the raw evidence](evidence/xstate.json).

## Measured execution overhead

macOS/Darwin 27.0.0 arm64, Node 24.19.0, Python 3.14.3. Thirty alternating paired runs,
three warm-ups per command; each measured command starts fresh processes. All three
scenarios are included per sample. Installation and report writing are excluded.
The native command runs one test file; replay starts Python and a fresh Node adapter
for each scenario. Those isolation/startup costs are part of the comparison.

| Command | Median | p95 (nearest rank) | Range |
| --- | ---: | ---: | ---: |
| Native `node --test` | 74.6 ms | 80.5 ms | 71.6–153.3 ms |
| interaction-check replay | 183.9 ms | 191.9 ms | 174.7–192.0 ms |

Replay is about **2.46× slower** for this small workload. There is no speed advantage
to advertise. These are descriptive local measurements, not a controlled multi-machine
benchmark or a prediction for another application. Raw samples are retained, including
the slowest samples. Reproduce on your machine (installation first):

```sh
python3 examples/xstate/verify.py --samples 30 --report local-evidence.json
```

## Does it detect wrong behavior?

The unchanged native tests and 3 traces pass. The verifier changes only the original
example model in temporary copies, then requires assertion failures in both paths:

| Deliberate defect in the example | Replay's first mismatch in selected trace | Native assertions |
| --- | --- | --- |
| CANCEL commits draft | Step 4, `context.saved` | Detects |
| Blank draft passes SAVE guard | Step 3, `can_save` | Detects |
| SAVE loses the text | Step 7 of restore trace, `context.saved` | Detects |

**3/3 selected mutations detected by both methods.** This small, hand-selected set
checks the evidence pipeline; it is not a mutation coverage percentage, an upstream
XState bug report, proof of superiority, or evidence that all regressions are caught.
Protocol errors/import failures do not count as successful mutation detection.

`--trace --report FILE` is the product change: a failure artifact carries the checked
prefix, event, expected fields, actual state and field differences. Reviewers can read
the sequence without running it first. Existing compact reports and JUnit remain usable.
Seven new runner tests cover this option, including invalid envelopes, Unicode, crashes
and continued reporting after a failed scenario. All 41 runner tests pass locally.

## Adoption decision

Use native tests when the case belongs to one codebase and ordinary assertions already
explain it. Use replay when a separately shareable event trace and a consistent report
help reproduce or exchange a regression. Runtime dependencies are not added to consumers:
Python and the adapter run during development/testing only.

For stronger real-application evidence, the previously proposed
[PdfCraft integration](https://github.com/storytold/pdfcraft/pull/4594) reproduces two
stale-draft regressions and replays ten UI/engine scenarios. Its source-policy approval
is still required; pins and passing tests do not settle that decision. See
[edit-session's adoption analysis](https://github.com/PerchAnton/edit-session/blob/edit-session/adoption-evidence/docs/ADOPTION.md).
New adapters are justified by a concrete workflow or regression, not their number.
