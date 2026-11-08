# 1.0.0 release

**Published on 8 November 2026.** The [release receipt](evidence/release-1.0.0.json)
records exact registry hashes, source/main commits, successful CI and clean consumer
checks. The [1.x commitment](COMPATIBILITY.md) preserves behavior from 0.1.0.

## Upgrade

Pin `interaction-check==1.0.0` in a virtual environment and
replay the host's scenarios with the same adapter revision. No JSON scenario or
adapter migration is intended. JSON report readers must accept extra fields and
check `schema`, not require an exact package version or parse console messages.
Python remains a development dependency; Rust adapters call the real Rust code.
This tool checks exposed state, not drawing, input delivery or accessibility.

## Release gates

- [x] Review the 1.x contract and confirm the only runner change is VERSION.
- [x] Pass the supported Python/OS matrix and native/adapted examples.
- [x] Run the installed-wheel gate against both published 0.1.0 and the 1.0.0
      candidate, including UTF-8 JSON with ASCII/cp1252 console output, mismatch
      prefixes, replay, trace and JUnit. Preserve expected failures.
- [x] Check the candidate wheel's three jsonpatch 1.39 scenarios separately from
      the existing published-version job. Keep both jobs.
- [x] Build wheel from sdist, check metadata and archive hashes, review and merge;
      require successful CI on main.
- [x] Obtain publication authorization, create a new v1.0.0 tag and use the existing
      PyPI Trusted Publishing workflow/environment approval.
- [x] Compare registry files/hashes and test the installed command before marking
      README, release notes or installation instructions as published.

Do not turn synthetic examples into claims of fewer production bugs or faster
development. PhotoCraft includes an adapter and scenarios; this does not establish
shared-CI adoption. A small native regression is often the simpler choice.

## Announcement draft (not sent)

interaction-check 1.0 defines compatible scenario, adapter and report formats.
Try Open → Type → Cancel: the example reports the first state mismatch, exports
the checked prefix with unchanged expectations and replays it. A native test catches
the same bug; the added value to evaluate is handing a reproducible case to someone
who uses another test environment. The adapter and Python runner have a maintenance cost.
