# prompt-toolkit external adapter

Experimental adapter maintained by PerchAnton. Upstream adoption is not claimed.
Source: [prompt-toolkit/python-prompt-toolkit@6c7fbc10](https://github.com/prompt-toolkit/python-prompt-toolkit/tree/6c7fbc1080dd331a031a2be1f96d4ebc0421f7ea), pinned in the dependency file/lockfile.

Calls the public Buffer API. Scenarios cover Unicode codepoint offsets, explicitly requested undo checkpoints, and validation. This does not run key bindings, async completion, a renderer, or a real terminal.

## Run

Python 3.12+ is used for Python widget adapters; the runner supports Python 3.10+. Go examples use Go 1.27.3 and Rust examples use Rust 1.99.1. From the repository root:

```sh
python -m pip install -r adapters/prompt-toolkit/requirements.txt
python interaction_check.py --timeout 30 scenarios/prompt-toolkit/*.json -- python adapters/prompt-toolkit/main.py
```

On Windows append `.exe` to Rust binaries. Use a temporary virtual environment/build directory and remove it after use. 3 scenarios / 21 steps; every scenario starts a fresh adapter process. Expected states stay in the runner, never in the adapter. JSONL requests are bounded to 64 KiB. These examples supplement each project's native suite. They are not a general terminal emulator or a promise of end-to-end application coverage.
