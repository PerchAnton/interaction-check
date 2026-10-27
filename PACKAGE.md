# interaction-check

A small Python command-line tool that replays semantic JSON event sequences against
an explicitly selected local adapter. Python 3.10+; **zero runtime dependencies**.
Licensed under MIT OR Apache-2.0. Experimental alpha: formats and CLI may still change.

## Installation

Install a published copy of this prerelease from PyPI:

```sh
python -m pip install 'interaction-check==0.1.0a7'
```

An exact version selects this prerelease without opting into all future prereleases.
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
- [Native tests or replay?](https://github.com/PerchAnton/interaction-check/blob/main/docs/CHOOSING.md)
- [Worked XState example](https://github.com/PerchAnton/interaction-check/tree/main/examples/xstate)
- [Moving a useful scenario into a native test](https://github.com/PerchAnton/interaction-check/blob/main/docs/NATIVE_TESTS.md)
- [Measured benefits and costs](https://github.com/PerchAnton/interaction-check/blob/main/docs/VALUE.md)

If a normal project test is simpler, keep that test. Replay is useful when sharing an
event sequence and a consistent report earns the adapter and runner maintenance cost.
