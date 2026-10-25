# textual external adapter

Experimental adapter maintained by PerchAnton. Upstream adoption is not claimed.
Source: [PerchAnton/textual@c22e522b](https://github.com/PerchAnton/textual/tree/c22e522b600d15e76b5c1048a07d1f09f937821f), pinned in the dependency file/lockfile.

Runs an actual App/Input with run_test and Pilot.press/resize_terminal. Covers Unicode, input restrictions and resize. This deliberately pins our proposed fix for [Textual #6745](https://github.com/Textualize/textual/issues/6745): the Unicode trace fails on upstream 5e5b7ef and passes on the fork. Upstream approval is pending; AI_POLICY requires approval before an upstream PR. No real terminal or screenshots are exercised.

## Run

Python 3.12+ is used for Python widget adapters; the runner supports Python 3.10+. Go examples use Go 1.27.3 and Rust examples use Rust 1.99.1. From the repository root:

```sh
python -m pip install -r adapters/textual/requirements.txt
python interaction_check.py --timeout 30 scenarios/textual/*.json -- python adapters/textual/main.py
```

On Windows append `.exe` to Rust binaries. Use a temporary virtual environment/build directory and remove it after use. 3 scenarios / 15 steps; every scenario starts a fresh adapter process. Expected states stay in the runner, never in the adapter. JSONL requests are bounded to 64 KiB. These examples supplement each project's native suite. They are not a general terminal emulator or a promise of end-to-end application coverage.
