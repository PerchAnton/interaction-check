# Alpha 2 review — 25 October 2026

Local environment: macOS arm64, Python 3.14.3. The runner remains standard-library-only.

## Reproduced defects

Using the previous runner at `dd112cd8ac29b834884cad0c4eb3ee793c74f10f`:

- A reply containing an unescaped U+2028 inside a JSON string failed with
  `Expected 1 replies, got 2`. Python's `splitlines()` also treats U+0085/U+2029 as
  separators, even though they are valid JSON string data. JSONL now splits only on LF.
- An unwritable report destination raised an uncaught exception after scenario output.
  Passing the scenario's own path to `--report` silently overwrote that scenario and exited 0.
  Output paths are now checked before adapter execution; reports use atomic replacement,
  and write failures produce an error diagnostic and exit 1.
- Deep nested state comparison could raise `RecursionError`. Both input and adapter JSON
  now have a documented maximum of 64 nested containers before recursive matching. Parser
  recursion errors are also reported normally on Python versions with recursive decoders.

## Checks

`python3 -m unittest -v`: **26 tests passed**. Regression coverage includes raw Unicode
separators, LF/CRLF and optional final LF, extra blank lines, nested JSON, invalid Unicode,
cyclic Python input, report aliases, preserved old reports after a failed replacement,
mixed successful/failed/malformed scenarios and parseable JUnit XML with escaped text.

The JUnit option is new: one test case per scenario, failures and successful-adapter stderr.
JSON and JUnit reports retain declared scenario names and source paths. XML-forbidden
control characters are replaced with U+FFFD without changing the JSON report.

The CI runner matrix covers Python 3.10 and 3.14 on Linux, plus Python 3.14 on Windows and
macOS. Results are available in [GitHub Actions](https://github.com/PerchAnton/interaction-check/actions);
the matrix declaration alone is not evidence that a pending run has passed.

## Compatibility with existing PhotoCraft consumers

The new runner passed against the retained macOS arm64 executables from the earlier
integration builds. Both JSON and JUnit reports were generated and parsed successfully:

| Adapter | Result | JSON report | Executable SHA-256 |
| --- | --- | --- | --- |
| Real Session opacity adapter | 8 scenarios / 41 steps passed | [Engine](../reports/alpha2-engine.json) | `c4ee4a29b634bda40faa5b1ceb74e3dccaaf7805c5e032a4a076784d4e69461e` |
| Edit Selected Guides UI adapter | 10 scenarios / 44 steps passed | [Guide editing](../reports/alpha2-guide-edit.json) | `61e5bc4fe4cd99a660e2b46832ef4e235b8bfd672f8062a47b5c368f08b35b71` |

The engine adapter uses PhotoCraft `14a4ab9b3f38f0b68fde6add97384919710374c8`.
The UI adapter was built from the proposed PhotoCraft integration at
`46b4a183d5f44035bbc216dcf6196701bcb45bc9`; run with `PHOTOCRAFT_LOCALE=en-US`.
Both binaries contain edit-session **alpha 1**, pinned to
`28620b8264660ea84a182110cf5894da90281c42`. They demonstrate compatibility of the new runner
with existing consumers, not a rebuilt application using the alpha 2 library API.

No PhotoCraft PR dependency pins were changed in this review. The library's new methods
were tested separately on Rust 1.88.0; see its
[validation record](https://github.com/PerchAnton/edit-session/blob/main/docs/VALIDATION.md).
PdfCraft integration, native input and rendering correctness are outside these checks.
