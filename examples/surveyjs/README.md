# SurveyJS Form Library: replayable model sequences

An external [interaction-check](../../README.md) example for [surveyjs/survey-library](https://github.com/surveyjs/survey-library).
Dependencies: **survey-core 3.2.2**; the lockfile records transitive versions and integrity hashes.

Reject navigation past a required question, clear a hidden answer, then complete, clear, and reuse a survey.

## Run

Requires Python 3.10+ and Node 24.15+. From this repository root:

```sh
npm --prefix examples/surveyjs ci --ignore-scripts --no-audit --no-fund
python examples/verify_consumers.py surveyjs
```

The verifier runs 2 native/control-boundary tests and 3 passing traces / 16 steps.
Reports are written to `.artifacts/consumer-reports/` with expected and actual state.
Each event is validated; expected states remain in the Python runner and are never passed to the adapter.

## Scope and limits

SurveyJS already has its own headless tester ([#11723](https://github.com/surveyjs/survey-library/pull/11723), merged).
Prefer that domain-specific harness for survey-only tests. This external example is kept for comparison;
it is not a proposal to add another runner dependency or a claim that SurveyJS lacks replay tooling.

Only the actual survey-core Model is driven. Framework renderers, accessibility, focus, and browser integration are not tested. detail_value explicitly reports null so object-subset matching cannot hide a retained answer.

The small fixture and adapter are original example code. The installed library implements the behavior.
This is not a report of an upstream bug unless separately identified. Existing native tests are preferable
for a small single-library regression; the extra runner is useful when a sequence needs a JSON report or
must be replayed against more than one consumer/version. Upstream adoption and release credit are pending.
