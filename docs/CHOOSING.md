# Start with the smallest useful test

interaction-check is a Python command-line tool. You write actions and expected
values in JSON. An adapter calls the program being tested and returns observed values.
The runner compares them and reports the first mismatch after the adapter has run.
It does not decide what correct behavior is, discover cases or record a GUI session.

## Choose the deliverable

| Your need | Start with |
| --- | --- |
| One regression in one repository | Its normal unit or integration test |
| A bug report that is easier to share as actions and expected states | A small replay case and a versioned adapter |
| A real widget, terminal or rendered-image check | The application's existing UI harness; an adapter may call it |
| Random input generation or minimization | An appropriate property-testing tool; this runner does neither |
| Preview/cancel/freshness logic in a Rust application | Evaluate the separate edit-session library or a local helper |

The [first example](../examples/quickstart/README.md) puts native tests beside replay.
Both catch its deliberate Cancel defect. Native assertions are simpler there; JSON
does not establish extra coverage, shorter total code or faster tests.

## What adopting replay costs

You maintain the adapter, selected state projection, scenario expectations, runtime
versions and setup instructions. A shared JSON format does not make one application's
events portable to an unrelated application. Comparing revisions requires a compatible
adapter and deliberate decisions about changes in expected behavior.

An external example can remain external. Running it in upstream CI is a separate
request: maintainers must consider extra runtimes, source policies and maintenance.
Installing our Python package does not install consumer libraries or adapters.

The two projects are independent:

| | interaction-check | edit-session |
| --- | --- | --- |
| Used by | A developer or test job | A Rust application's edit flow |
| Does | Compares adapter observations with a JSON case | Holds a draft and checks host-supplied value/context |
| Does not | Edit a document or provide Undo | Run scenarios, render UI or own Undo |
| Required companion | An explicit local adapter | Host validation, revision tracking and command dispatch |
| Can work alone? | Yes, without edit-session | Yes, without interaction-check or Python |

## What the feedback changed

The [current-source Rust example](../examples/tui-input/README.md) shows four real
tui-input actions beside a short native test, including a reproducible first
mismatch and export. It makes the runner's role visible without asserting extra
coverage. The rat-salsa maintainer preferred interactive examples for complex
behavior and declined the extra runner; that decision does not call for another
integration proposal.

For a real-library walkthrough and expected/observed diagrams, see
[python-dispatch](../examples/dispatch/README.md). For the precise scope of the terminal
widget proposal, see [rat-salsa](REAL_API_WALKTHROUGH.md). The pyee native scenario is
already in [PR #228](https://github.com/jfhbrook/pyee/pull/228); no duplicate is needed.

| Question from maintainers | Concrete response in this repository |
| --- | --- |
| [Redux: what problem and upstream change?](https://github.com/reduxjs/redux/discussions/4962#discussioncomment-19203020) | Use the decision table above. Current core-store examples justify no change to Redux's CI. |
| [Microsoft Edit: what does this tool do?](https://github.com/microsoft/edit/discussions/993#discussioncomment-19203218) | One runnable example with actions, an actual method call, an expectation and a visible mismatch. |
| [Eldiron: why not a Rust test?](https://github.com/markusmoenig/Eldiron/discussions/87#discussioncomment-19209675) | Keep a native baseline beside the replay case and state the additional setup cost. |
| [pyee: a normal test may be enough](https://github.com/jfhbrook/pyee/issues/226#issuecomment-6409488443) | [Native-test audit](../examples/pyee/README.md) and manual handoff; keeping a runner dependency is optional. |
| [bat: CI report was too long](https://github.com/sharkdp/bat/pull/4095#issuecomment-6425239682) | [Report one concrete result](REPORTING.md), with raw details linked separately. |
| [python-json-patch: a small documentation PR](https://github.com/stefankoegl/python-json-patch/issues/239#issuecomment-6427353952) | [PR #243](https://github.com/stefankoegl/python-json-patch/pull/243) uses jsonpatch directly; no runner dependency is proposed. |

These links explain design choices, not endorsements. Contributions, proposed
integrations and adoption are different facts. A useful outcome can be a small native
test or a documentation example, even when the consumer never installs our tool.
