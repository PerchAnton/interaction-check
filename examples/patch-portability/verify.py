"""Replay installed packages; preserve known mismatches instead of calling them passes."""
import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def verify(output, go_adapter=None, rust_adapter=None, fixed_jsonpath=None):
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    records = []
    for library in ["jsonpath", "jsonpatch", "immutable", "merge"] + (["go"] if go_adapter else []) + (["rust"] if rust_adapter else []) + (["jsonpath-fixed"] if fixed_jsonpath else []):
        command = (["node", str(HERE / "node_adapter.mjs")] if library == "immutable" else
                   [sys.executable, str(HERE / "python_adapter.py"), "jsonpath" if library == "jsonpath-fixed" else library])
        if library == "go": command = [str(go_adapter.resolve())]
        if library == "rust": command = [str(rust_adapter.resolve())]
        names = (["merge-null-array-idempotence"] if library == "merge" else
                 ["move-and-escaped-key", "failed-batch-publication", "boolean-is-not-number", "native-unicode-pointer"])
        if library == "rust": names += ["merge-null-array-idempotence"]
        if (HERE / "scenarios/producer.json").exists() and library != "merge": names += ["producer"]
        env = dict(os.environ)
        if library == "jsonpath-fixed": env["PYTHONPATH"] = str(fixed_jsonpath.resolve())
        for name in names:
            report = output / f"{library}-{name}.json"
            run = subprocess.run([sys.executable, "-m", "interaction_check", "--trace", "--report", str(report),
                                  str(HERE / "scenarios" / f"{name}.json"), "--", *command],
                                 capture_output=True, text=True, encoding="utf-8", timeout=30, cwd=HERE, env=env)
            expected_mismatch = library == "jsonpath" and name == "boolean-is-not-number"
            if run.returncode != (1 if expected_mismatch else 0):
                raise AssertionError(f"{library}/{name}: {run.stdout}\n{run.stderr}")
            data = json.loads(report.read_text())
            if expected_mismatch:
                last = data['results'][0]['trace'][-1]
                if last['step'] != 2 or not any('state.error' in x for x in last['differences']):
                    raise AssertionError(f"Wrong mismatch: {last}")
            records.append({"library": library, "scenario": name, "exit_code": run.returncode,
                            "known_mismatch": expected_mismatch, "report": report.name,
                            "sha256": hashlib.sha256(report.read_bytes()).hexdigest()})
    evidence = {"schema": 1, "scope": "Application adapters; no upstream adoption or full RFC conformance claim",
                "packages": {p: importlib.metadata.version(p) for p in
                             ['interaction-check', 'python-jsonpath', 'jsonpatch', 'json-merge-patch']},
                "node_packages": json.loads((HERE / 'package-lock.json').read_text())['packages']['']['dependencies'],
                "source_sha256": {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in HERE.rglob('*') if p.is_file() and not any(x in p.parts for x in ['node_modules', 'target', '__pycache__'])},
                "go_modules": (HERE / 'go.mod').read_text(), "rust_manifest": (HERE / 'rust/Cargo.toml').read_text(),
                "records": records}
    (output / 'index.json').write_text(json.dumps(evidence, indent=2) + '\n')
    print(f"{len(records)} reports retained; known boolean mismatch is a failed trace, not a passing library result.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--go-adapter', type=Path)
    parser.add_argument('--rust-adapter', type=Path)
    parser.add_argument('--fixed-jsonpath', type=Path)
    args = parser.parse_args()
    verify(args.output, args.go_adapter, args.rust_adapter, args.fixed_jsonpath)
