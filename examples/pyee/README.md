# A native test can be the useful result

The [pyee maintainer suggested a test](https://github.com/jfhbrook/pyee/issues/226#issuecomment-6409488443)
instead of a larger documentation example. We checked all seven test modules at
[`cbeca176`](https://github.com/jfhbrook/pyee/tree/cbeca176af1161e8fb52ea7bdc5e8133952358d2/tests)
and translated one external trace into [one native pytest test](test_once_reentrant.py).
The [complete candidate and findings were posted for review](https://github.com/jfhbrook/pyee/issues/226#issuecomment-6411419260).
No upstream acceptance or merge is claimed.

## What it checks

A synchronous `once` listener emits the same event from inside its callback. It must
already be removed, so it runs once; the persistent listener receives the nested event
before the outer emission resumes, and remains registered for later events. The nested
emit is bounded by `value == 1`, so a regression fails an assertion rather than recursing
forever. The test uses public APIs and the project's existing pytest setup.

The existing `test_once`, removal tests and Trio's `test_once_multiple_pending_emits`
cover different paths. The other two external pyee traces largely repeat existing
no-listener/removal and error behavior; we did not propose duplicate tests for them.
Async scheduling, threading and performance are outside this candidate's scope.

## Evidence, not a current pyee bug

26 October 2026, CPython 3.12.13, macOS arm64. All seven upstream test modules ran,
with no skips. The source is pinned above, not whatever a later `main` contains.

| Source | Original suite | Suite + candidate |
| --- | --- | --- |
| Unchanged pyee | 53 pass | 54 pass |
| Deliberate local mutation | 53 pass; mutation escapes detection | 53 pass, **candidate fails** |

The [mutation](../../docs/evidence/pyee/remove-after-callback.patch) moves removal of
the once listener until after its callback returns. Under that deliberately incorrect
version, the log contains a second `once` invocation. The added test detects this
specific gap; it is not a general mutation score, coverage percentage, speedup or
bug found in released pyee. Current pyee already behaves correctly.

**No interaction-check dependency is needed by the native test.** The general runner
and its JSON protocol are not used in this audit. The value of the external example
here is helping isolate a small assertion that fits the maintainer's existing suite.
The native candidate, not an extra framework, is the proposed contribution.

[Raw results](../../docs/evidence/pyee/results.json) ·
[baseline log](../../docs/evidence/pyee/baseline-original-suite.log) ·
[extended baseline](../../docs/evidence/pyee/baseline-with-candidate.log) ·
[mutation without candidate](../../docs/evidence/pyee/mutated-original-suite.log) ·
[mutation with candidate](../../docs/evidence/pyee/mutated-with-candidate.log).
Logs normalize temporary paths and trailing whitespace; test counts come from JUnit XML.

## Reproduce

Use Python 3.12+ and a local checkout of this repository. From its root:

```sh
git clone https://github.com/jfhbrook/pyee.git .artifacts/pyee-source
git -C .artifacts/pyee-source checkout cbeca176af1161e8fb52ea7bdc5e8133952358d2
python3.12 -m venv .venv-pyee
# Activate the environment for your platform, then:
python -m pip install -c .artifacts/pyee-source/requirements_dev.txt -r examples/pyee/requirements-audit.txt
python examples/pyee/verify.py --source .artifacts/pyee-source --output .artifacts/pyee-audit
```

The six direct requirements are the upstream test tools and runtimes; transitive
versions are constrained by the pinned upstream file. They are optional audit
dependencies, not core runner dependencies. No package installation happens in
`verify.py`. It reads the pinned Git archive, runs four isolated suites and changes only
temporary source copies. Any unexpected test error, skip, failure or collection count
makes the command fail; success requires that only the candidate detects the mutation.
Use a fresh output directory for each audit. The recorded snapshot is separate from
the live CI badge. The candidate and audit were AI-assisted.
