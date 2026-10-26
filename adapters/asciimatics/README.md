# asciimatics external adapter

Experimental adapter maintained by PerchAnton. Upstream adoption is not claimed.
Source: [peterbrittain/asciimatics@bf0cea87](https://github.com/peterbrittain/asciimatics/tree/bf0cea87b50439e40a5c7b708d64da4195314a60), pinned in the dependency file/lockfile.

Calls Text.process_event with native KeyboardEvent values and observes public value, validity, and change callbacks. Covers maximum length, readonly behavior, validation and no-op callbacks. No Frame/Screen is created, so this does not test rendering, mouse coordinates, or terminal backends.

## Run

Python 3.12+ is used for Python widget adapters; the runner supports Python 3.10+. Go examples use Go 1.27.3 and Rust examples use Rust 1.99.1. From the repository root:

```sh
python -m pip install -r adapters/asciimatics/requirements.txt
python interaction_check.py --timeout 30 scenarios/asciimatics/*.json -- python adapters/asciimatics/main.py
```

On Windows append `.exe` to Rust binaries. Use a temporary virtual environment/build directory and remove it after use. 3 scenarios / 15 steps; every scenario starts a fresh adapter process. Expected states stay in the runner, never in the adapter. JSONL requests are bounded to 64 KiB. These examples supplement each project's native suite. They are not a general terminal emulator or a promise of end-to-end application coverage.
