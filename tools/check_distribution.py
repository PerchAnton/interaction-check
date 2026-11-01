"""Install one built wheel in a fresh venv and test the CLI away from the checkout."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import venv
import xml.etree.ElementTree as ET


def run(*command, cwd, expected=0):
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != expected:
        raise RuntimeError(f"{command!r}: {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def main():
    wheels = list(Path(sys.argv[1] if len(sys.argv) > 1 else "dist").glob("*.whl"))
    if len(wheels) != 1:
        raise SystemExit("Expected exactly one wheel in the distribution directory")
    wheel = wheels[0].resolve()
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        environment = root / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        binary = environment / ("Scripts" if os.name == "nt" else "bin")
        python = binary / ("python.exe" if os.name == "nt" else "python")
        cli = binary / ("interaction-check.exe" if os.name == "nt" else "interaction-check")
        run(str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheel), cwd=root)
        metadata = json.loads(run(str(python), "-I", "-c", '''import json
from importlib.metadata import metadata, version
import interaction_check
m = metadata("interaction-check")
assert not m.get_all("Requires-Dist")
assert m["License-Expression"] == "MIT OR Apache-2.0"
assert version("interaction-check") == interaction_check.VERSION
print(json.dumps({"version": interaction_check.VERSION, "module": interaction_check.__file__}))
''', cwd=root))
        if environment.resolve() not in Path(metadata["module"]).resolve().parents:
            raise RuntimeError("Imported source checkout instead of installed package")
        if run(str(cli), "--version", cwd=root).strip() != "interaction-check " + metadata["version"]:
            raise RuntimeError("Installed CLI version differs from package metadata")
        adapter = root / "echo.py"
        adapter.write_text('''import json, sys
for line in sys.stdin:
    r = json.loads(line)
    print(json.dumps({"protocol": 1, "id": r["id"], "state": r["event"]}))
''', encoding="utf-8")
        scenario = {"schema": 1, "name": "installed CLI", "steps": [
            {"event": {"n": 1}, "expect": {"n": 1}},
            {"event": {"n": 2}, "expect": {"n": 3}},
            {"event": {"n": 4}, "expect": {"n": 4}},
        ]}
        (root / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")
        run(str(cli), "--failure-dir", "failures", "--report", "report.json", "--trace",
            "--junit", "report.xml", "scenario.json", "--", str(python),
            str(adapter), cwd=root, expected=1)
        report = json.loads((root / "report.json").read_text(encoding="utf-8"))
        assert report["schema"] == 1 and report["version"] == metadata["version"]
        result, = report["results"]
        assert result["passed"] is False and result["failure_step"] == 2
        assert result["source"] == "scenario.json" and result["name"] == "installed CLI"
        assert [entry["step"] for entry in result["trace"]] == [1, 2]
        assert result["trace"][1]["expect"] == {"n": 3}
        assert result["trace"][1]["actual"] == {"n": 2}
        assert ET.parse(root / "report.xml").getroot().get("failures") == "1"
        prefix = json.loads((root / "failures/0001.json").read_text(encoding="utf-8"))
        if prefix["steps"] != scenario["steps"][:2]:
            raise RuntimeError("Installed CLI exported the wrong prefix")
        output = run(str(cli), "failures/0001.json", "--", str(python), str(adapter),
                     cwd=root, expected=1)
        if "Step 2" not in output:
            raise RuntimeError("Export did not reproduce the state mismatch")
        scenario["steps"][1]["expect"]["n"] = 2
        (root / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")
        run(str(cli), "--report", "report.json", "--junit", "report.xml", "scenario.json",
            "--", str(python), str(adapter), cwd=root)
        result, = json.loads((root / "report.json").read_text(encoding="utf-8"))["results"]
        assert result["passed"] is True and result["steps"] == 3
        assert "failure_step" not in result and "trace" not in result
        assert ET.parse(root / "report.xml").getroot().get("failures") == "0"
        print(f"Installed {metadata['version']}: metadata, JSON/JUnit contract, PASS, export and replay verified")


if __name__ == "__main__":
    main()
