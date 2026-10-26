"""Expand Python consumer scenarios portably on Linux, Windows and macOS."""

import argparse
import pathlib
import subprocess
import sys

from factory import MODULES

ROOT = pathlib.Path(__file__).resolve().parents[2]


def main():
    """Run each native consumer in fresh processes and preserve failures."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--reports", type=pathlib.Path)
    args = parser.parse_args()
    if args.reports:
        args.reports.mkdir(parents=True, exist_ok=True)
    status = 0
    for consumer in MODULES:
        command = [
            sys.executable,
            str(ROOT / "interaction_check.py"),
            "--timeout",
            "30",
        ]
        if args.reports:
            command += ["--report", str(args.reports / f"{consumer}.json")]
        scenarios = sorted((ROOT / "scenarios" / consumer).glob("*.json"))
        if not scenarios:
            raise RuntimeError(f"no scenarios for {consumer}")
        command += [str(p) for p in scenarios]
        command += [
            "--",
            sys.executable,
            str(ROOT / "adapters/python-libraries/main.py"),
            consumer,
        ]
        if subprocess.run(command, cwd=ROOT, check=False).returncode:
            # A signal is a negative return code on POSIX; it is still a failure.
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
