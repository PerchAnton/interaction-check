# Share one result people can act on

Start with the affected behavior and one reproducible command. Keep the report short
enough that a maintainer can see the question before opening logs:

```text
Case: Cancel should preserve the saved title.
Observed: step 3 returned saved="Preview"; expected "Original".
Reproduce: <exact command, runner version and adapter revision>
Attachment: <scenario with original expectations; say whether it was rerun>
Request: <one concrete question or proposed native test>
```

The values above come from our deliberately broken teaching model, not an upstream
bug. Use your actual result. [Run the complete example](../examples/quickstart/README.md).

Put a JSON report, complete stderr and environment details in an attachment or a
collapsed section. For a CI problem, link the failing run and relevant step first.
A separate successful diagnostic run does not make the original required check pass.
Do not substitute a long list of unrelated passing tests for the requested evidence.

Before sending an exported case, rerun it with the same adapter revision and retain
the original expectations. Say whether the failure is an assertion, an adapter crash,
a timeout or a protocol error. Only an assertion mismatch has a checked failing state.
The entire batch may already have executed, even if the report ends earlier.

Report only values needed to reproduce the problem. Review attachments for private
document contents and paths. A public report need not include the full document when
a small synthetic example demonstrates the same behavior.
