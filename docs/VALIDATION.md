# Validation evidence

## Alpha 4: reviewable trace evidence — 26 October 2026

- 41 runner tests pass locally (34 existing + 7 trace-report tests). The new cases were
  added before the feature; 5 failed with the previous API/CLI and pass after implementation.
- `--trace --report FILE` records the checked prefix and mismatching observed state,
  preserving strict JSONL validation, expectation isolation and compact default reports.
- The focused XState example passes 3 scenarios / 18 steps and 6 Node tests. Both native
  assertions and replay detect all 3 deliberately changed example behaviors. These are
  controlled mutations in our model, not bugs found in XState.
- A fresh build of PdfCraft's adapter at `255a4e87c320ff0c7007008fb9a62dac6eaf8551`
  passes all 10 scenarios / 79 steps with the new trace option. The
  [report](evidence/pdfcraft-alpha4.json) contains actual states and the built executable's
  hash. Rust 1.99.1/macOS arm64, English locale, system fonts disabled. The full app suite
  was not repeated for this runner change; consumer dependency pins are unchanged.
- [Value analysis](VALUE.md) includes all 30 paired timing samples, source counts and
  install scope. Native tests are faster here; no speed or total-code reduction is claimed.

The new `Replay evidence` workflow checks the focused example and mutations on Linux,
Windows and macOS. A local pass is not a claim that remote CI has completed.

## Alpha 3 runner review - 25 October 2026

Local environment: macOS arm64, Python 3.12. The runner is still standard-library-only.

On the preceding main `11b728e33ee2c5ef27a918e778e311a856a87af4`, three new regression
tests failed: stdout/stderr exceeding 1 MiB followed by a stalled adapter reached the
timeout instead of failing early, and assertion/protocol failures lost stderr in the
Python API and JSON/JUnit reports.

After the changes, all **34 tests pass**. They cover early output-limit detection on both
streams, fast exits, the exact byte boundary, a non-reading adapter with large input,
partial diagnostics on timeout, failure diagnostics in both report formats, and the
previous protocol/Unicode/JSON/report-preservation cases.

The runner checks output sizes about every 50 ms and reaps the direct process on failure.
Capture stays file-backed and reads are bounded. Polling is not a hard disk quota or
subprocess-tree isolation; adapter children remain the adapter's responsibility.

No PhotoCraft/PdfCraft source or dependency pin changed. Full application builds and GUI
scenarios were not rerun locally for this review; the existing PhotoCraft engine CI job
tests the updated runner against its pinned real adapter. Its result is reported by CI,
not inferred from the unit tests above. Temporary local test files are removed.

## PdfCraft consumer proposal — 25 October 2026

[PR #4594](https://github.com/storytold/pdfcraft/pull/4594), consumer commit `535d990d10832baf3b0a64910c51b280c224bd5c` on upstream
`418ac6a2af49b7ac2fed44ca2cae8d5d1d2cec0d`, uses edit-session alpha 2 at
`033f7c3a67b825b8f222288788cc61234c0c945d` and interaction-check at
`7722d66c0ede7855ff58d1df3d1632fd4e5e66a5`.

On macOS arm64, Rust 1.99.1, Python 3.14.3, English UI and system-font fallback disabled:

- Two upstream UI regressions fail before the fix: confirming a stale title after another
  edit, and confirming after edit + Undo back to the same original value.
- 522 unit, 1,153 integration and 3 performance tests pass for `pdfcraft-ui-egui`; 11
  existing tests are ignored. Tests run with two threads and host loopback/GPU access.
- Formatting, strict Clippy on all UI targets, layering, asset attribution and parity pass.
- `xtask wasm` checks 31 crates successfully, with warnings in unchanged platform-specific code.
- 10 JSONL scenarios / 79 steps pass through actual egui controls and the real engine.
  They cover commit, Cancel/Escape, no-op preserving Redo, custom validation, stale edits,
  Undo ABA, reload, target switching/closure, clean inspection refresh, and save/reopen.
  JSON and JUnit reports were generated. Actual Description, Custom, Initial View and
  stale-notice screenshots were inspected locally; synthetic PDF bytes are not committed.
- Engine refusal/retry is atomic. A separate test checks freshness immediately at commit,
  without relying on a preceding frame. Pending input is not rebased by an inspection tab.

The [consumer documentation](https://github.com/PerchAnton/pdfcraft/blob/535d990d10832baf3b0a64910c51b280c224bd5c/docs/document-properties-sessions.md)
explains replay and the proposed exact Git-source exception. These results are local;
Linux/Windows CI, native OS input, another PDF reader, packaging and maintainer adoption
are not implied. PhotoCraft's existing alpha 1 pin is unchanged.

# Alpha 2 runner review — 25 October 2026

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

`python3 -m unittest -v`: **27 tests passed**. Regression coverage includes raw Unicode
separators, LF/CRLF and optional final LF, extra blank lines, nested JSON, invalid Unicode,
cyclic Python input, report aliases, preserved old reports after a failed replacement,
mixed successful/failed/malformed scenarios, printable diagnostics for malformed duplicate
keys and parseable JUnit XML with escaped text.

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
