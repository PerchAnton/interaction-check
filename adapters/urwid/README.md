# urwid external adapter

Experimental adapter maintained by PerchAnton. Upstream adoption is not claimed.
Source: [urwid/urwid@864dfc2b](https://github.com/urwid/urwid/tree/864dfc2b7cffa8fb660ba7c0f18b5e1ea39921c2), pinned in the dependency file/lockfile.

Calls Edit.keypress and Edit.render at bounded widths. Covers Unicode edits, multiline joins, resize, and rejected controls. Urwid is separately installed under LGPL-2.1; this original adapter contains no copied Urwid source and does not relicense or vendor Urwid. It does not run MainLoop or a terminal backend. Existing upstream #1188 addresses a separate full-line cursor issue.

## Run

Python 3.12+ is used for Python widget adapters; the runner supports Python 3.10+. Go examples use Go 1.27.3 and Rust examples use Rust 1.99.1. From the repository root:

```sh
python -m pip install -r adapters/urwid/requirements.txt
python interaction_check.py --timeout 30 scenarios/urwid/*.json -- python adapters/urwid/main.py
```

On Windows append `.exe` to Rust binaries. Use a temporary virtual environment/build directory and remove it after use. 3 scenarios / 17 steps; every scenario starts a fresh adapter process. Expected states stay in the runner, never in the adapter. JSONL requests are bounded to 64 KiB. These examples supplement each project's native suite. They are not a general terminal emulator or a promise of end-to-end application coverage.
