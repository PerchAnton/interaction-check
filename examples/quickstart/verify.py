"""Verify pass -> deliberate defect -> export -> replay, beside native tests."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(command, *, cwd, expected=0, stdin=None):
    result = subprocess.run(command, cwd=cwd, input=stdin, text=True,
                            capture_output=True, timeout=30, check=False)
    if result.returncode != expected:
        raise RuntimeError(f"Unexpected exit {result.returncode}: {command!r}\n"
                           f"{result.stdout}\n{result.stderr}")
    return result


def verify(installed=False):
    runner = [sys.executable, "-m", "interaction_check"] if installed else [
        sys.executable, str(ROOT / "interaction_check.py")]
    scenarios = sorted((HERE / "scenarios").glob("*.json"))
    with tempfile.TemporaryDirectory(prefix="interaction-check-example-") as folder:
        work = Path(folder)
        for name in ("editor.py", "adapter.py", "native_tests.py"):
            shutil.copyfile(HERE / name, work / name)
        adapter = [sys.executable, "-B", str(work / "adapter.py")]
        native = [sys.executable, "-B", "-m", "unittest", "-v", "native_tests"]
        passing = run(native, cwd=work)
        assert "Ran 3 tests" in passing.stderr and "\nOK" in passing.stderr
        run(runner + ["--trace", "--report", "pass.json", *map(str, scenarios),
                      "--", *adapter], cwd=work)
        passed = json.loads((work / "pass.json").read_text())["results"]
        assert len(passed) == 3 and all(r["passed"] for r in passed)
        assert sum(r["steps"] for r in passed) == 12

        # Change only our original teaching model, in the temporary copy.
        source = (work / "editor.py").read_text()
        before = "    def cancel(self):\n        self.draft = None"
        after = "    def cancel(self):\n        self.saved = self.draft\n        self.draft = None"
        assert source.count(before) == 1
        (work / "editor.py").write_text(source.replace(before, after))
        broken = run(native, cwd=work, expected=1)
        assert "FAIL: test_cancel_keeps_saved" in broken.stderr
        assert "FAILED (failures=1)" in broken.stderr and "ERROR:" not in broken.stderr
        failure = run(runner + ["--trace", "--report", "fail.json", "--failure-dir",
                               "failures", *map(str, scenarios), "--", *adapter],
                      cwd=work, expected=1)
        failed = json.loads((work / "fail.json").read_text())["results"]
        assert [r["passed"] for r in failed] == [False, True, True]
        assert failed[0]["trace"][-1]["step"] == 3
        mismatch = failed[0]["trace"][-1]
        assert mismatch["expect"]["saved"] == "Original"
        assert mismatch["actual"]["saved"] == "Preview"
        assert mismatch["differences"] == ["state.saved: expected 'Original', got 'Preview'"]
        original = json.loads(scenarios[0].read_text())
        exported = json.loads((work / "failures/0001.json").read_text())
        assert exported == dict(original, steps=original["steps"][:3])
        assert len(list((work / "failures").iterdir())) == 1
        replayed = run(runner + ["failures/0001.json", "--", *adapter],
                       cwd=work, expected=1)
        assert "Step 3" in replayed.stdout and "state.saved" in replayed.stdout

        # Show why a checked prefix is not a claim of stopped execution.
        requests = "".join(json.dumps({"protocol": 1, "id": i, "event": s["event"]})
                           + "\n" for i, s in enumerate(original["steps"], 1))
        replies = run(adapter, cwd=work, stdin=requests).stdout.splitlines()
        assert len(replies) == 4 and json.loads(replies[-1])["id"] == 4
        assert json.loads(replies[-1])["state"]["draft"] == "Preview"
        print(failure.stdout.split("  Scenario:")[0].strip())
        report = {
            "recorded_date": datetime.now(timezone.utc).date().isoformat(),
            "scope": "Original teaching model; no upstream bug or adoption claim",
            "python": platform.python_version(), "system": platform.system(),
            "runner": "installed package" if installed else "source checkout",
            "native": {"baseline_passed": 3, "mutant_passed": 2, "mutant_failures": 1, "mutant_errors": 0},
            "replay": {"baseline_passed": 3, "baseline_steps": 12, "mutant_passed": 2, "mutant_failures": 1},
            "mutation": "Cancel incorrectly writes the draft to the saved title",
            "first_mismatch": mismatch,
            "batch_execution": {"events_processed": 4, "checked_prefix_steps": 3},
            "export": {"steps": 3, "preserves_expectations": True, "rerun_same_mismatch": True},
            "source_hash_format": "SHA-256 of UTF-8 text with LF line endings",
            "source_files": {str(p.relative_to(ROOT)).replace("\\", "/"):
                             hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
                             for p in [ROOT / "interaction_check.py", HERE / "verify.py",
                                       HERE / "editor.py", HERE / "adapter.py", HERE / "native_tests.py", *scenarios]},
        }
        return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--installed", action="store_true", help="use this Python's installed package")
    args = parser.parse_args()
    report = verify(args.installed)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Verified: native 3/3; replay 3/3 (12 steps); both catch the deliberate Cancel defect.")
    print("Export: 3 checked steps, original expectations, same mismatch on rerun.")


if __name__ == "__main__":
    main()
