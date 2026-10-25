"""Replay semantic JSONL scenarios against an explicitly selected local adapter.

No shell, sleeps, network client, GUI automation, or application dependency is required.
Each scenario gets a fresh adapter process. Expected results are never sent to it.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

VERSION = "0.1.0-alpha.2"
LIMIT = 1024 * 1024
MAX_DEPTH = 64


class CheckError(Exception):
    pass


def validate_json(value):
    """Bound nesting before recursive comparison/encoding, including Python API input."""
    pending = [(value, 1)]
    while pending:
        item, depth = pending.pop()
        if type(item) in (dict, list):
            if depth > MAX_DEPTH:
                raise CheckError(f"JSON nesting exceeds {MAX_DEPTH} containers")
            if isinstance(item, dict):
                if any(type(key) is not str for key in item):
                    raise CheckError("JSON object keys must be strings")
                pending.extend((key, depth + 1) for key in item)
                pending.extend((child, depth + 1) for child in item.values())
            else:
                pending.extend((child, depth + 1) for child in item)
        elif type(item) is str:
            try:
                item.encode("utf-8")
            except UnicodeError as error:
                raise CheckError("JSON strings must contain valid Unicode scalar values") from error
        elif type(item) is float:
            if not math.isfinite(item):
                raise CheckError("JSON numbers must be finite")
        elif item is not None and type(item) not in (bool, int):
            raise CheckError(f"Unsupported JSON value type: {type(item).__name__}")


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
        value = json.loads(text, parse_constant=reject, parse_float=finite_float,
                           object_pairs_hook=unique_object)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise CheckError(f"Invalid JSON: {error}") from error
    validate_json(value)
    return value


def validate(scenario):
    validate_json(scenario)
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
    """Objects are subsets even inside arrays; array length/order and scalar types match."""
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
    try:
        payload = "".join(json.dumps({"protocol": 1, "id": i, "event": step["event"]},
                                    ensure_ascii=False, allow_nan=False) + "\n"
                          for i, step in enumerate(scenario["steps"], 1)).encode("utf-8")
    except (ValueError, UnicodeError, RecursionError) as error:
        raise CheckError(f"Cannot encode scenario: {error}") from error
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
            # JSONL is delimited by LF, not Unicode line separators inside strings.
            lines = output.read().decode("utf-8").split("\n")
            if lines[-1] == "":
                lines.pop()  # A single final LF is optional; extra blank lines are errors.
        except UnicodeError as error:
            raise CheckError("Adapter output is not UTF-8") from error
    if len(lines) != len(scenario["steps"]):
        raise CheckError(f"Expected {len(scenario['steps'])} replies, got {len(lines)}")
    for index, (line, step) in enumerate(zip(lines, scenario["steps"]), 1):
        try:
            response = strict_json(line)
        except CheckError as error:
            raise CheckError(f"Step {index}: {error}") from error
        if (not isinstance(response, dict) or type(response.get("protocol")) is not int
                or response["protocol"] != 1 or type(response.get("id")) is not int
                or response["id"] != index or not isinstance(response.get("state"), dict)):
            raise CheckError(f"Step {index}: invalid envelope or mismatched reply id")
        errors = differences(step["expect"], response["state"])
        if errors:
            raise CheckError(f"Step {index} ({step['event']}): " + "; ".join(errors))
    return {"name": scenario["name"], "passed": True, "steps": len(lines), "stderr": stderr}


def check_report_paths(destinations, scenarios):
    """Catch accidental input replacement and overlapping outputs before running adapters."""
    previous = list(scenarios)
    for destination in destinations:
        for other in previous:
            if (destination.resolve() == other.resolve()
                    or (destination.exists() and other.exists() and destination.samefile(other))):
                raise CheckError(f"Report path overlaps an input or another report: {destination}")
        previous.append(destination)


def write_report(path, content):
    """Replace only a complete report; a failed write leaves the previous file intact."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n",
                                         dir=path.parent, prefix=f".{path.name}.",
                                         suffix=".tmp", delete=False) as output:
            temporary = Path(output.name)
            output.write(content)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def junit_report(results):
    def xml_text(value):
        # JSON and stderr may include control characters that XML 1.0 cannot represent.
        return "".join(char if (char in "\t\n\r" or " " <= char <= "\ud7ff"
                               or "\ue000" <= char <= "\ufffd" or "\U00010000" <= char <= "\U0010ffff")
                       else "\ufffd" for char in value)

    suite = ET.Element("testsuite", name="interaction-check", tests=str(len(results)),
                       failures=str(sum(not result["passed"] for result in results)), errors="0")
    for result in results:
        case = ET.SubElement(suite, "testcase", name=xml_text(result["name"]),
                             classname="interaction-check", file=xml_text(result["source"]))
        if not result["passed"]:
            failure = ET.SubElement(case, "failure", message=xml_text(result["error"]),
                                    type="CheckError")
            failure.text = xml_text(result["error"])
        if result.get("stderr"):
            ET.SubElement(case, "system-err").text = xml_text(result["stderr"])
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(suite, encoding="unicode") + "\n"


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--report", type=Path, help="write a JSON report atomically")
    parser.add_argument("--junit", type=Path, help="write a JUnit XML report atomically")
    parser.add_argument("scenarios", nargs="+", type=Path)
    if "--" not in argv:
        parser.error("Separate the adapter command with --")
    boundary = argv.index("--")
    args = parser.parse_args(argv[:boundary])
    command = argv[boundary + 1:]
    if not command or not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("Specify an adapter command and a positive finite timeout")
    try:
        check_report_paths([path for path in (args.report, args.junit) if path], args.scenarios)
    except (CheckError, OSError, RuntimeError) as error:
        parser.error(str(error))
    results = []
    for path in args.scenarios:
        name = path.name
        try:
            if path.stat().st_size > LIMIT:
                raise CheckError("Scenario exceeds 1 MiB")
            scenario = strict_json(path.read_text(encoding="utf-8"))
            if isinstance(scenario, dict) and isinstance(scenario.get("name"), str) and scenario["name"].strip():
                name = scenario["name"]
            result = replay(scenario, command, args.timeout)
        except (CheckError, OSError, UnicodeError) as error:
            result = {"name": name, "passed": False, "error": str(error)}
        result["source"] = str(path)
        results.append(result)
        print(("PASS " if result["passed"] else "FAIL ") + result["name"])
        if not result["passed"]:
            print("  " + result["error"])
    report_failed = False
    for destination, render in [
        (args.report, lambda: json.dumps({"version": VERSION, "results": results},
                                        ensure_ascii=False, indent=2) + "\n"),
        (args.junit, lambda: junit_report(results)),
    ]:
        if destination:
            try:
                write_report(destination, render())
            except (OSError, UnicodeError) as error:
                print(f"ERROR writing report {destination}: {error}", file=sys.stderr)
                report_failed = True
    return 0 if not report_failed and all(result["passed"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
