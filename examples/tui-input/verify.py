"""Run the same four actions through a native Rust test and JSON replay."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def run(command, expected=0):
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True,
                            timeout=300, check=False)
    if result.returncode != expected:
        raise RuntimeError(f"Unexpected exit {result.returncode}: {command!r}\n"
                           f"{result.stdout}\n{result.stderr}")
    return result


def main():
    manifest = str(HERE / "Cargo.toml")
    run(["cargo", "test", "--locked", "--manifest-path", manifest, "--test", "native"])
    run(["cargo", "build", "--locked", "--manifest-path", manifest])
    metadata = json.loads(run(["cargo", "metadata", "--locked", "--no-deps",
                               "--format-version", "1", "--manifest-path", manifest]).stdout)
    binary = Path(metadata["target_directory"]) / "debug" / (
        "interaction-check-tui-input.exe" if os.name == "nt" else "interaction-check-tui-input")
    runner = [sys.executable, str(ROOT / "interaction_check.py")]
    source = json.loads((HERE / "graphemes.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="interaction-check-tui-") as folder:
        work = Path(folder)
        passing = work / "pass.json"
        run(runner + ["--trace", "--report", str(passing), str(HERE / "graphemes.json"), "--", str(binary)])
        good = json.loads(passing.read_text())["results"]
        assert len(good) == 1 and good[0]["passed"] and good[0]["steps"] == 4
        # A deliberately wrong expectation, not a change to tui-input or a discovered bug.
        source["steps"][3]["expect"]["value"] = "xe\u0301界"
        wrong = work / "wrong.json"
        wrong.write_text(json.dumps(source, ensure_ascii=False), encoding="utf-8")
        report = work / "fail.json"
        exports = work / "failures"
        failed = run(runner + ["--trace", "--report", str(report), "--failure-dir",
                              str(exports), str(wrong), "--", str(binary)], expected=1)
        result = json.loads(report.read_text())["results"][0]
        mismatch = result["trace"][-1]
        assert not result["passed"] and mismatch["step"] == 4
        assert mismatch["actual"]["value"] == "x界"
        assert mismatch["differences"] == ["state.value: expected 'xé界', got 'x界'"]
        assert json.loads((exports / "0001.json").read_text()) == source
        replay = run(runner + [str(exports / "0001.json"), "--", str(binary)], expected=1)
        assert "Step 4" in replay.stdout and "state.value" in replay.stdout
        print(failed.stdout.strip())
    print("Verified: native Rust test passed; replay passed 4 steps; wrong expectation fails at step 4 and replays.")


if __name__ == "__main__":
    main()
