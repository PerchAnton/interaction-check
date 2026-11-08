# CLI and report compatibility for 1.x

## Maintenance and versioning

This is the compatibility contract for **1.0.0 and the 1.x series**.
The earlier 0.1.0 contract remains available on the v0.1.0 tag.
Version 1.0 introduces a compatibility commitment, without changing runtime behavior.

Follow [Semantic Versioning 2.0](https://semver.org/spec/v2.0.0.html): patches fix
bugs while preserving the documented contract; minor releases add compatible
features or deprecations; incompatible changes require a new major and migration
notes. Deprecations document a replacement and remain available throughout 1.x.
Changes to defaults, error semantics, minimum platforms or existing input limits
are breaking when they invalidate supported consumers. Internal details and the
exclusions below are outside this contract. A bug fix restores documented behavior;
it must include a reproducer and describe any changed result.

Maintenance by PerchAnton is best effort, targeting the latest 1.x release once
published. Older releases remain downloadable, not separate maintenance branches.
There is no SLA, fixed support term or independent security audit. Report defects
with exact versions and synthetic inputs, without secrets or personal documents.
Application owners remain responsible for native regression tests and rollout.

## Supported interface

- Python >=3.10, no runtime dependencies; explicit local adapter command after `--`.
- Scenario `schema: 1` and JSONL `protocol: 1` retain the existing event/envelope
  rules. Each scenario starts a fresh process; only events, not expectations, go
  to the adapter. Object expectations are recursive subsets, including inside
  arrays; array order/length matter, numbers compare by value, booleans remain
  distinct from numbers. Unknown envelope fields are ignored, missing required
  fields and wrong protocol/id types are errors.
- Existing CLI options remain. Exit 0 means all scenarios and requested report
  writes succeeded; 1 means a check/run/report failure; 2 means invalid invocation
  or report destination setup. Human console/error prose is not a parseable API.
- The scenario and JSONL limits remain 1 MiB and 64 nested containers. Time/output
  checks stop the direct child, not its descendants; polling is not a disk quota.
  This executes trusted code, not a sandbox. The full event batch may execute
  before the runner observes a mismatch.

## JSON report schema 1

`--report` includes `schema: 1` next to `version` (the package version) and `results`
(ordered one-per-input scenario). This is separate from scenario schema/protocol.
Readers must accept additional fields and reject unsupported report schema versions.
Alpha reports lack `schema`; treat those as legacy reports explicitly, not as proof
that an arbitrary schema is supported.

Every result has `name`, `source`, and boolean `passed`. Success also has `steps`
and `stderr`. Failure has `error`; `stderr` is present if available and nonempty.
`failure_step`, when present, is the **1-based first state mismatch**. It is absent
for success, malformed input/protocol, timeout and adapter crashes; do not infer an
index by parsing `error`. `failure_scenario` means a mismatch prefix was written;
`export_error` means that write failed. Exported expectations are never rewritten.

With `--trace`, checked entries contain `step`, `event`, `expect`, `actual`, `passed`,
and `differences` on mismatches. A partial trace may end before a protocol failure;
absence of a trace is not evidence of zero adapter actions. Exported prefixes need
a separate rerun; they are not minimized cases or evidence of stopped execution.
JUnit retains one testcase per input and failure/system-err details; XML-invalid
control characters are replaced. Exact formatting and timings are not contractual.

## Migration and scope

After publication, upgrade with `interaction-check==1.0.0`. Existing
schema-1 scenarios/adapters do not need changes. JSON consumers should handle the
two additive fields without comparing complete objects or parsing message prose.
The installed-wheel gate checks reports, trace, JUnit, failure export and replay
outside the checkout. Native/JSON examples, Mermaid output and the existing
Python/OS matrix remain required. Internal Python helpers and prototype adapters
are outside this contract; they are not automatically accepted upstream.

The runner behavior is unchanged from 0.1.0 apart from its reported package
version. Existing schema-1 scenarios and protocol-1 adapters need no migration.
Keep report schema 1 separate from the package version. Never reuse a published
version.

## CI approval

We can provide an exact runner/archive hash, license/dependency inventory, native
test comparison, adapter scope and a patch for the project's shared workflow.
Maintainers decide whether to execute the runner, which source and workflow to
use, and the job's permissions/maintenance owner. Keep existing source gates;
neither a pinned commit, green tests nor release status grants this approval.

## Version 1 boundaries

The supported entry points are the installed `interaction-check` command and
`python -m interaction_check`. Importing implementation functions is not a public
Python library API. Preserve all existing flags, the 5-second default timeout,
exit-code meanings and schema-1/protocol-1 behavior throughout 1.x. Python 3.10
remains the minimum. New optional report fields are additive; removing fields,
changing types/meanings, or no longer accepting schema-1 scenarios/protocol-1
adapters requires a major. A future schema may be opt-in only if schema 1 remains
the default. Console prose, timings and XML formatting are not machine interfaces.
