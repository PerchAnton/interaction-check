# interaction-check

This page documents **1.0.0**. Check the [release status](https://github.com/PerchAnton/interaction-check/releases/tag/v1.0.0) for registry availability.

Version **1.0.0** preserves Unicode JSON reports even when the terminal uses ASCII or Windows-1252. See the [CLI/report compatibility contract](https://github.com/PerchAnton/interaction-check/blob/main/docs/COMPATIBILITY.md).

A small Python command-line tool that replays semantic JSON event sequences against
an explicitly selected local adapter. Python 3.10+; **zero runtime dependencies**.
Licensed under MIT OR Apache-2.0. The 1.x CLI and report compatibility policy is linked above.

## Installation

Install the release from PyPI:

```sh
python -m pip install 'interaction-check==1.0.0'
```

Use an exact version and run your adapter regressions before upgrading.
Use a virtual environment. On Windows, the same command works with `py -m pip`.
For other distribution options and current publication status, see the
[project README](https://github.com/PerchAnton/interaction-check#install-the-released-command).

## Usage

```sh
interaction-check --version
interaction-check --failure-dir failures --trace --report report.json scenario.json -- path/to/adapter
```

The adapter is a trusted program you select; it receives events as JSONL and returns
states. Expected states are never sent to it. Each scenario starts a fresh process.
The runner is not a sandbox and does not download or discover adapters automatically.

`--failure-dir` creates a **new** directory containing numbered JSON scenarios through
the first state mismatch. Expectations stay unchanged. These are checked prefixes, not
automatically minimized or independently verified reproductions. Re-run an export with
the same adapter revision. Crashes, timeouts and malformed protocol replies do not
produce a guessed state-mismatch scenario.

The installed wheel contains the runner and its licenses. Examples and application
adapters remain in the repository and may have their own dependencies. The separate
Rust library edit-session is not required.

- [Scenario and adapter protocol](https://github.com/PerchAnton/interaction-check#scenario-format)
- [First example: no application or extra packages](https://github.com/PerchAnton/interaction-check/tree/main/examples/quickstart)
- [Real callbacks and Mermaid diagrams](https://github.com/PerchAnton/interaction-check/tree/v0.1.0-alpha.8/examples/dispatch)
- [Native tests or replay?](https://github.com/PerchAnton/interaction-check/blob/main/docs/CHOOSING.md)
- [Worked XState example](https://github.com/PerchAnton/interaction-check/tree/main/examples/xstate)
- [Moving a useful scenario into a native test](https://github.com/PerchAnton/interaction-check/blob/main/docs/NATIVE_TESTS.md)
- [Measured benefits and costs](https://github.com/PerchAnton/interaction-check/blob/main/docs/VALUE.md)

If a normal project test is simpler, keep that test. Replay is useful when sharing an
event sequence and a consistent report earns the adapter and runner maintenance cost.
