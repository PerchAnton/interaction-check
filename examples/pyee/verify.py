"""Compare pyee's native suite and one candidate against a controlled mutation."""

import argparse
import difflib
import hashlib
import json
import platform
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

REVISION = "cbeca176af1161e8fb52ea7bdc5e8133952358d2"
HERE = Path(__file__).resolve().parent
BEFORE = """                    if event in self._events and f in self._events[event]:
                        self._remove_listener(event, f)
                    else:
                        return None
                # f may return a coroutine, so we need to return that
                # result here so that emit can schedule it
                return f(*args, **kwargs)"""
AFTER = """                    if event not in self._events or f not in self._events[event]:
                        return None
                result = f(*args, **kwargs)
                with self._lock:
                    self._remove_listener(event, f)
                return result"""


def verify(source, output):
    """Read the pinned Git snapshot; only disposable copies are mutated."""
    candidate = HERE / "test_once_reentrant.py"
    if (output / "results.json").exists():
        raise FileExistsError("Choose a fresh output directory for this audit")
    output.mkdir(parents=True, exist_ok=True)
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "upstream_revision": REVISION,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "mutation": "Remove once listener after callback returns, instead of before "
        "callback begins. Deliberate local mutation, not an upstream bug.",
        "candidate_sha256": hashlib.sha256(candidate.read_bytes()).hexdigest(),
        "runs": [],
    }
    with tempfile.TemporaryDirectory(prefix="pyee-native-evidence-") as temp:
        temp = Path(temp)
        archive = temp / "source.tar"
        subprocess.run(
            [
                "git",
                "-C",
                str(source),
                "archive",
                "--format=tar",
                "-o",
                str(archive),
                REVISION,
            ],
            check=True,
        )
        for mode in ("baseline", "mutated"):
            root = temp / mode
            root.mkdir()
            with tarfile.open(archive) as source_tar:
                source_tar.extractall(root, filter="data")
            path = root / "pyee/base.py"
            original = path.read_text(encoding="utf-8")
            if original.count(BEFORE) != 1:
                raise RuntimeError("Pinned mutation anchor is missing or ambiguous")
            mutated = original.replace(BEFORE, AFTER)
            if mode == "mutated":
                path.write_text(mutated, encoding="utf-8")
                diff = difflib.unified_diff(
                    original.splitlines(True),
                    mutated.splitlines(True),
                    fromfile="a/pyee/base.py",
                    tofile="b/pyee/base.py",
                )
                (output / "remove-after-callback.patch").write_text(
                    "".join(diff), encoding="utf-8"
                )
            for added in (False, True):
                name = mode + ("-with-candidate" if added else "-original-suite")
                if added:
                    (root / "tests/test_once_reentrant_candidate.py").write_bytes(
                        candidate.read_bytes()
                    )
                xml = temp / (name + ".xml")
                result = subprocess.run(
                    [
                        sys.executable,
                        "-B",
                        "-m",
                        "pytest",
                        "tests",
                        "-o",
                        "addopts=-q",
                        "--junitxml=" + str(xml),
                    ],
                    cwd=root,
                    text=True,
                    capture_output=True,
                    timeout=60,
                )
                log = result.stdout + result.stderr
                (output / (name + ".log")).write_text(
                    log.replace(str(temp), "<temporary-directory>"), encoding="utf-8"
                )
                suite = ET.parse(xml).getroot().find("testsuite")
                if suite is None:
                    raise RuntimeError("pytest did not produce a test suite")
                record = {
                    "name": name,
                    "returncode": result.returncode,
                    **{
                        key: int(suite.get(key, "0"))
                        for key in ("tests", "failures", "errors", "skipped")
                    },
                    "failed_tests": [
                        case.get("name")
                        for case in suite.findall("testcase")
                        if case.find("failure") is not None
                    ],
                }
                report["runs"].append(record)
                expected_failure = mode == "mutated" and added
                expected_names = (
                    ["test_once_is_removed_before_reentrant_emit"]
                    if expected_failure
                    else []
                )
                if (
                    result.returncode != int(expected_failure)
                    or record["errors"]
                    or record["skipped"]
                    or record["failures"] != int(expected_failure)
                    or record["failed_tests"] != expected_names
                ):
                    raise RuntimeError(f"Unexpected result for {name}: {record}\n{log}")
                print(json.dumps(record))
    counts = [run["tests"] for run in report["runs"]]
    if counts[0] < 1 or counts != [counts[0], counts[0] + 1, counts[0], counts[0] + 1]:
        raise RuntimeError(f"Unexpected test collection: {counts}")
    (output / "results.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="Local clone containing the pinned pyee commit",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Directory for results, logs and mutation patch",
    )
    args = parser.parse_args()
    verify(args.source.resolve(), args.output.resolve())
