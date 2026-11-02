"""Run the three jsonpatch scenarios with the installed beta runner."""
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
    args = parser.parse_args()
    if version("jsonpatch") != "1.39":
        parser.error("install the versions in examples/jsonpatch/requirements.txt")
    scenarios = sorted((HERE / "scenarios").glob("*.json"))
    with tempfile.TemporaryDirectory() as directory:
        report = args.report if args.report is not None else Path(directory) / "report.json"
        # Isolated mode imports the package installed in this interpreter's environment.
        subprocess.run([sys.executable, "-I", "-m", "interaction_check", "--report",
                        str(report), *map(str, scenarios), "--", sys.executable, "-I",
                        str(HERE / "adapter.py")], check=True)
        data = json.loads(report.read_text(encoding="utf-8"))
    if data["version"] != "0.1.0b1" or data["schema"] != 1:
        raise SystemExit("expected a schema-1 report from interaction-check 0.1.0b1")
    if [r["steps"] for r in data["results"]] != [3, 3, 3]:
        raise SystemExit("expected three checked scenarios with three steps each")
    print("Passed 3 scenarios / 9 steps on jsonpatch 1.39 with interaction-check 0.1.0b1.")


if __name__ == "__main__":
    main()
