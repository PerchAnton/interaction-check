# promptkit external adapter

Experimental adapter maintained by PerchAnton. Upstream adoption is not claimed.
Source: [erikgeiser/promptkit@15b4c35e](https://github.com/erikgeiser/promptkit/tree/15b4c35efed7f3703895e175c6bd66a83c5fccbb), pinned in the dependency file/lockfile.

Runs native textinput.Model Init/Update/View. Covers Unicode, validation/submission, length limits, resize and Ctrl+C cancellation. Blink commands are not scheduled; only an Enter completion command is inspected for QuitMsg. This does not run a terminal, completion, or selection widgets. Existing upstream #39 concerns selection scrolling and is not duplicated.

## Run

Python 3.12+ is used for Python widget adapters; the runner supports Python 3.10+. Go examples use Go 1.27.3 and Rust examples use Rust 1.99.1. From the repository root:

```sh
(cd adapters/promptkit && go test -race ./... && go vet ./... && go build -o probe.exe .)
python interaction_check.py --timeout 30 scenarios/promptkit/*.json -- adapters/promptkit/probe.exe
```

On Windows append `.exe` to Rust binaries. Use a temporary virtual environment/build directory and remove it after use. 3 scenarios / 15 steps; every scenario starts a fresh adapter process. Expected states stay in the runner, never in the adapter. JSONL requests are bounded to 64 KiB. These examples supplement each project's native suite. They are not a general terminal emulator or a promise of end-to-end application coverage.
