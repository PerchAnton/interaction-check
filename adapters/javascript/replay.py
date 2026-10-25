"""Replay every JavaScript consumer with the same command on all CI platforms."""

import argparse
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONSUMERS = (
    "slate", "lexical", "tiptap", "quill", "immer", "zustand",
    "xstate", "yjs", "automerge", "redux-toolkit",
    "mobx", "jotai", "valtio", "nanostores", "effector", "pinia", "vue-reactivity", "rxjs", "final-form", "tanstack-store",
    "zod", "valibot", "yup", "ajv", "joi", "superstruct", "arktype", "vest", "immutable-js", "reselect", "redux", "preact-signals", "solid", "svelte", "robot", "eventemitter3", "formkit", "redux-saga", "redux-observable", "react-hook-form",
)


def main():
    """Keep scenario expansion out of the shell and preserve runner failures."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", default=shutil.which("node"))
    parser.add_argument("--reports", type=pathlib.Path)
    args = parser.parse_args()
    if not args.node:
        parser.error("Node.js is required")
    if args.reports:
        args.reports.mkdir(parents=True, exist_ok=True)
    status = 0
    for consumer in CONSUMERS:
        command = [sys.executable, str(ROOT / "interaction_check.py"), "--timeout", "30"]
        if args.reports:
            command += ["--report", str(args.reports / f"{consumer}.json")]
        command += [str(p) for p in sorted((ROOT / "scenarios" / consumer).glob("*.json"))]
        command += ["--", args.node, str(ROOT / "adapters/javascript/main.mjs"), consumer]
        result = subprocess.run(command, cwd=ROOT, check=False)
        status = max(status, result.returncode)
    return status


if __name__ == "__main__":
    sys.exit(main())
