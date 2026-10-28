"""Run native controls, replay traces, and the explicitly known reset regression.

Dependencies are installed independently with npm ci in each example directory.
This runs models and public library APIs, not graphical user interfaces.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SUPPORTED = ("cytoscape", "rete", "surveyjs", "tanstack-form", "xyflow",
             "diagram-js", "grapesjs", "fabric", "vee-validate", "excalidraw")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("example", choices=SUPPORTED)
    parser.add_argument("--output", type=Path, default=ROOT / ".artifacts/consumer-reports")
    args = parser.parse_args()
    example = ROOT / "examples" / args.example
    args.output.mkdir(parents=True, exist_ok=True)
    if args.example == "excalidraw":
        subprocess.run(["node", str(example / "build.mjs")], cwd=ROOT, check=True, timeout=120)
    native = subprocess.run(["node", "--test", str(example / "native.test.mjs")],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=120)
    print(native.stdout, end="")
    if native.stderr:
        print(native.stderr, file=sys.stderr, end="")
    if native.returncode:
        return native.returncode
    command = [sys.executable, str(ROOT / "interaction_check.py"), "--timeout", "30", "--trace"]
    report = args.output / (args.example + ".json")
    replay = subprocess.run([*command, "--report", str(report),
                             *map(str, sorted((example / "scenarios").glob("*.json"))),
                             "--", "node", str(example / "main.mjs")], cwd=ROOT, timeout=150)
    if replay.returncode:
        return replay.returncode
    if args.example == "tanstack-form":
        regression = args.output / "tanstack-form-known-reset-failure.json"
        result = subprocess.run([*command, "--report", str(regression),
                                 str(example / "regressions/03-pending-reset-regression.json"),
                                 "--", "node", str(example / "main.mjs")], cwd=ROOT, timeout=60)
        data = json.loads(regression.read_text(encoding="utf-8"))["results"]
        if len(data) != 1 or result.returncode != 1 or data[0]["passed"]:
            raise RuntimeError("The pinned TanStack reset baseline changed; investigate, do not update the expectation blindly")
        last = data[0]["trace"][-1]
        if last["step"] != 5 or last["actual"]["errors"] != ["error for the old value"]:
            raise RuntimeError("Regression failed for an unexpected reason")
        print("VERIFIED KNOWN FAILURE: reset receives an error for the old value at step 5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
