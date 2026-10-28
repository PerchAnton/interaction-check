"""Run real API/native checks and a deliberately wrong expectation; save or check evidence."""
import argparse
import copy
import hashlib
from importlib.metadata import version
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from interaction_check import CheckError, replay  # noqa: E402
from render import render  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", str(HERE),
                    "-p", "native_tests.py", "-v"], check=True)
    case = json.loads((HERE / "scenario.json").read_text(encoding="utf-8"))
    command = [sys.executable, str(HERE / "adapter.py")]
    correct = replay(case, command, trace=True)
    wrong = copy.deepcopy(case)
    wrong["steps"][1]["expect"]["log"] = [1, 2, 3, 4]
    try:
        replay(wrong, command, trace=True)
    except CheckError as error:
        assert error.failure_step == 2
        assert error.trace[-1]["actual"] == {"count": 4, "log": [1, 4]}
        failed = {"passed": False, "error": str(error), "trace": error.trace}
    else:
        raise AssertionError("deliberately wrong expectation was not caught")
    sources = [HERE / n for n in ["adapter.py", "native_tests.py", "scenario.json", "render.py", "verify.py", "requirements.txt"]]
    evidence = {"package": f"python-dispatch=={version('python-dispatch')}",
                "native_tests": 3, "synthetic_wrong_expectation": True,
                "source_sha256": {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(
                    p.read_text(encoding='utf-8').encode()).hexdigest() for p in sources},
                "results": [correct, failed]}
    outputs = {ROOT / "docs/evidence/dispatch.json": json.dumps(evidence, indent=2) + "\n",
               HERE / "trace.md": render(correct), HERE / "mismatch.md": render(failed)}
    for path, text in outputs.items():
        if args.check:
            assert path.read_text(encoding="utf-8") == text, f"stale evidence: {path}"
        else:
            path.write_text(text, encoding="utf-8")
    print("3 native tests; 5 replay steps; deliberate wrong expectation detected at step 2.")


if __name__ == "__main__":
    main()
