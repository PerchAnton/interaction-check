"""Verify real adapters and require precise mismatches from unmodified dependency behavior."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from producer import scenario
from render import render

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def replay(paths, command, output, expected=0):
    process = subprocess.run([sys.executable, str(ROOT / "interaction_check.py"), "--trace", "--report", str(output),
                              *map(str, paths), "--", *command], capture_output=True, text=True, encoding="utf-8", timeout=30)
    if process.returncode != expected:
        raise RuntimeError(process.stdout + process.stderr)
    return json.loads(output.read_text(encoding="utf-8"))


def verify(output):
    output.parent.mkdir(parents=True, exist_ok=True)
    results = {}
    with tempfile.TemporaryDirectory(prefix="interop-") as directory:
        temporary = Path(directory)
        generated = temporary / "python-produced.json"
        generated.write_text(json.dumps(scenario()), encoding="utf-8")
        for family in ("patch", "history", "events"):
            paths = sorted((HERE / "scenarios").glob(f"{family}-*.json"))
            if family == "patch": paths.append(generated)
            good = replay(paths, ["node", str(HERE / "main.mjs"), family], temporary / "report.json")
            if family == "patch":
                reference = replay(paths, [sys.executable, str(HERE / "patch-reference.py")], temporary / "reference.json")
                a = [[row["actual"] for row in r["trace"]] for r in good["results"]]
                b = [[row["actual"] for row in r["trace"]] for r in reference["results"]]
                if a != b: raise AssertionError("Python and Mutative observations differ")
                results["python_reference"] = reference
            bad_file, step, field = {"patch": ("patch-move.json", 2, "state.document"),
                "history": ("history-invalid.json", 3, "state.missing"),
                "events": ("events-names.json", 5, "state.callbacks")}[family]
            bad = replay([HERE / "scenarios" / bad_file], ["node", str(HERE / "main.mjs"), family + "-raw"], temporary / "raw.json", 1)
            failed = bad["results"][0]["trace"][-1]
            if failed["step"] != step or not any(field in line for line in failed["differences"]):
                raise AssertionError(f"unexpected {family} failure: {failed}")
            results[family] = {"adapted": good, "raw_failure": bad}
        (output.parent / "events-adapted.md").write_text(render(results["events"]["adapted"]), encoding="utf-8")
        (output.parent / "events-raw.md").write_text(render(results["events"]["raw_failure"]), encoding="utf-8")
    hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted([*HERE.glob("*.mjs"), *HERE.glob("*.py"), HERE / "package-lock.json",
                               HERE / "requirements.txt", * (HERE / "scenarios").glob("*.json")])}
    output.write_text(json.dumps({"schema": 1, "scope": "Examples, not upstream patches or performance measurements",
        "source_hashes": hashes, "results": results}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("Verified: Python/Mutative agree; three raw dependency mismatches detected at the required steps.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    verify(parser.parse_args().report)
