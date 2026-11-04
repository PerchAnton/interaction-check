"""Run the three jsonpatch scenarios with an explicitly versioned installed runner."""
import argparse
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, help="keep the runner's JSON report")
    parser.add_argument("--expected-version", default="0.1.0b1",
                        help="expected installed runner (default: published beta baseline)")
    args = parser.parse_args()
    if version("jsonpatch") != "1.39":
        parser.error("install the versions in examples/jsonpatch/requirements.txt")
    if version("interaction-check") != args.expected_version:
        parser.error("installed interaction-check differs from --expected-version")
    scenarios = sorted((HERE / "scenarios").glob("*.json"))
    with tempfile.TemporaryDirectory() as directory:
        report = args.report if args.report is not None else Path(directory) / "report.json"
        # Isolated mode imports the package installed in this interpreter's environment.
        subprocess.run([sys.executable, "-I", "-m", "interaction_check", "--report",
                        str(report), *map(str, scenarios), "--", sys.executable, "-I",
                        str(HERE / "adapter.py")], check=True)
        data = json.loads(report.read_text(encoding="utf-8"))
    if data["version"] != args.expected_version or data["schema"] != 1:
        raise SystemExit(f"expected a schema-1 report from interaction-check {args.expected_version}")
    if not all(r["passed"] for r in data["results"]):
        raise SystemExit("all three scenarios must pass")
    if [r["steps"] for r in data["results"]] != [3, 3, 3]:
        raise SystemExit("expected three checked scenarios with three steps each")
    print(f"Passed 3 scenarios / 9 steps on jsonpatch 1.39 with interaction-check {args.expected_version}.")


if __name__ == "__main__":
    main()
