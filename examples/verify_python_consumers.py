"""Verify one isolated Python consumer using the current Python environment."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("example", choices=("pyqtgraph", "napari", "toga"))
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/consumer-reports")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    example = ROOT / "examples" / args.example
    commands = [
        [sys.executable, str(ROOT / "examples/test_python_protocol.py")],
        [sys.executable, str(example / "test_native.py")],
        [sys.executable, str(ROOT / "interaction_check.py"), "--timeout", "60", "--trace",
         "--report", str(args.output / (args.example + ".json")),
         *map(str, sorted((example / "scenarios").glob("*.json"))),
         "--", sys.executable, str(example / "adapter.py")],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=ROOT, timeout=240)
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
