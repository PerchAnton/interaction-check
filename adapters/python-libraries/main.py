"""Run one optional Python library fixture through the bounded JSONL protocol."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from factory import MODULES, create
from python_protocol import serve


def main():
    """Select an explicit adapter; expectations remain only in the runner."""
    parser = argparse.ArgumentParser()
    parser.add_argument("consumer", choices=MODULES)
    args = parser.parse_args()
    serve(create(args.consumer).step)


if __name__ == "__main__":
    main()
