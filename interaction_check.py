"""Replay semantic JSONL scenarios against an explicitly selected local adapter.

No shell, sleeps, network client, GUI automation, or application dependency is required.
Each scenario gets a fresh adapter process. Expected results are never sent to it.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile

VERSION = "0.1.0-alpha.1"
LIMIT = 1024 * 1024


class CheckError(Exception):
    pass


def strict_json(text):
    def reject(value):
        raise CheckError(f"Non-JSON numeric constant: {value}")
    def finite_float(value):
        result = float(value)
        if not math.isfinite(result):
            raise CheckError(f"Number is outside the finite JSON range: {value}")
        return result
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise CheckError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    try:
        return json.loads(text, parse_constant=reject, parse_float=finite_float,
                          object_pairs_hook=unique_object)
    except (ValueError, UnicodeError) as error:
        raise CheckError(f"Invalid JSON: {error}") from error


def validate(scenario):
    if not isinstance(scenario, dict) or type(scenario.get("schema")) is not int or scenario["schema"] != 1:
        raise CheckError("Scenario must declare schema: 1")
    if not isinstance(scenario.get("name"), str) or not scenario["name"].strip():
        raise CheckError("Scenario needs a nonempty name")
    steps = scenario.get("steps")
    if not isinstance(steps, list) or not steps:
        raise CheckError("Scenario needs at least one step")
    for index, step in enumerate(steps, 1):
        if not isinstance(step, dict) or set(step) != {"event", "expect"}:
            raise CheckError(f"Step {index}: use exactly event and expect")
        if not isinstance(step["event"], dict) or not isinstance(step["expect"], dict) or not step["expect"]:
            raise CheckError(f"Step {index}: event and nonempty expect must be objects")


def differences(expected, actual, path="state"):
    """Object expectations are subsets; arrays and scalar types are exact."""
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{path}: expected an object, got {actual!r}"]
        errors = []
        for key, value in expected.items():
            if key not in actual:
                errors.append(f"{path}.{key}: missing")
            else:
                errors.extend(differences(value, actual[key], f"{path}.{key}"))
        return errors
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(expected) != len(actual):
            return [f"{path}: expected {expected!r}, got {actual!r}"]
        return [error for i, (a, b) in enumerate(zip(expected, actual))
                for error in differences(a, b, f"{path}[{i}]")]
    both_numbers = type(expected) in (int, float) and type(actual) in (int, float)
    if (not both_numbers and type(expected) is not type(actual)) or expected != actual:
        return [f"{path}: expected {expected!r}, got {actual!r}"]
    return []


def replay(scenario, command, timeout=5.0):
    validate(scenario)
    if not command or not math.isfinite(timeout) or timeout <= 0:
        raise CheckError("A command and a positive finite timeout are required")
    payload = "".join(json.dumps({"protocol": 1, "id": i, "event": step["event"]},
                                ensure_ascii=False, allow_nan=False) + "\n"
                      for i, step in enumerate(scenario["steps"], 1)).encode("utf-8")
    if len(payload) > LIMIT:
        raise CheckError("Scenario exceeds 1 MiB")
    # File-backed capture avoids unbounded RAM if an adapter logs too much. Adapters are
    # trusted local test programs, not sandboxed plugins; no subprocess isolation is claimed.
    with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as diagnostic:
        try:
            completed = subprocess.run(command, input=payload, stdout=output, stderr=diagnostic,
                                       timeout=timeout, check=False)
        except subprocess.TimeoutExpired as error:
            raise CheckError(f"Adapter timed out after {timeout:g}s") from error
        except OSError as error:
            raise CheckError(f"Cannot run adapter: {error}") from error
        if output.tell() > LIMIT or diagnostic.tell() > LIMIT:
            raise CheckError("Adapter output exceeds 1 MiB")
        output.seek(0)
        diagnostic.seek(0)
        stderr = diagnostic.read().decode("utf-8", errors="replace")
        if completed.returncode:
            raise CheckError(f"Adapter exited with {completed.returncode}: {stderr[-2000:]}")
        try:
            lines = output.read().decode("utf-8").splitlines()
        except UnicodeError as error:
            raise CheckError("Adapter output is not UTF-8") from error
    if len(lines) != len(scenario["steps"]):
        raise CheckError(f"Expected {len(scenario['steps'])} replies, got {len(lines)}")
    for index, (line, step) in enumerate(zip(lines, scenario["steps"]), 1):
        response = strict_json(line)
        if (not isinstance(response, dict) or type(response.get("protocol")) is not int
                or response["protocol"] != 1 or type(response.get("id")) is not int
                or response["id"] != index or not isinstance(response.get("state"), dict)):
            raise CheckError(f"Step {index}: invalid envelope or mismatched reply id")
        errors = differences(step["expect"], response["state"])
        if errors:
            raise CheckError(f"Step {index} ({step['event']}): " + "; ".join(errors))
    return {"name": scenario["name"], "passed": True, "steps": len(lines), "stderr": stderr}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--report", type=Path)
    parser.add_argument("scenarios", nargs="+", type=Path)
    if "--" not in argv:
        parser.error("Separate the adapter command with --")
    boundary = argv.index("--")
    args = parser.parse_args(argv[:boundary])
    command = argv[boundary + 1:]
    if not command or not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("Specify an adapter command and a positive finite timeout")
    results = []
    for path in args.scenarios:
        try:
            if path.stat().st_size > LIMIT:
                raise CheckError("Scenario exceeds 1 MiB")
            result = replay(strict_json(path.read_text(encoding="utf-8")), command, args.timeout)
        except (CheckError, OSError, UnicodeError) as error:
            result = {"name": path.name, "passed": False, "error": str(error)}
        results.append(result)
        print(("PASS " if result["passed"] else "FAIL ") + result["name"])
        if not result["passed"]:
            print("  " + result["error"])
    if args.report:
        args.report.write_text(json.dumps({"version": VERSION, "results": results},
                                         ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
