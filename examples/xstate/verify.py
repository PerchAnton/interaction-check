"""Reproduce traces and controlled model mutations; optionally measure local overhead.

No upstream XState bug is claimed. Timings include process startup, not installation.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from interaction_check import VERSION, main, write_report  # noqa: E402


def run(command):
    started = time.perf_counter_ns()
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                            encoding="utf-8", timeout=30, check=False)
    return result, (time.perf_counter_ns() - started) / 1_000_000


def measure(samples):
    return {"samples_ms": samples, "n": len(samples), "median_ms": statistics.median(samples),
            "p95_ms": sorted(samples)[math.ceil(0.95 * len(samples)) - 1],
            "min_ms": min(samples), "max_ms": max(samples)}


def files_stats(paths):
    return {str(path.relative_to(ROOT)): {
        "bytes": len(path.read_bytes()),
        "physical_lines": len(path.read_text(encoding="utf-8").splitlines()),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    } for path in paths}


def verify():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", default="node")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=0,
                        help="0 skips timing; otherwise at least 10 alternating paired samples")
    args = parser.parse_args()
    if args.samples != 0 and args.samples < 10:
        parser.error("use 0 or at least 10 samples")
    node = shutil.which(args.node)
    if not node:
        parser.error("Node.js was not found")
    scenarios = sorted((HERE / "scenarios").glob("*.json"))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    # The original model and traces never change. Temporary copies resolve XState from
    # this example's parent node_modules, on Windows too (no symlink permission needed).
    with tempfile.TemporaryDirectory(prefix=".verification-", dir=HERE) as folder:
        temporary = Path(folder)
        native = [node, "--test", str(HERE / "native.test.mjs")]
        replay = [sys.executable, str(ROOT / "interaction_check.py"),
                  *map(str, scenarios), "--", node, str(HERE / "main.mjs")]
        native_result, _ = run(native)
        if native_result.returncode:
            raise RuntimeError(native_result.stdout + native_result.stderr)
        observed = temporary / "observed.json"
        code = main(["--trace", "--report", str(observed), *map(str, scenarios),
                     "--", node, str(HERE / "main.mjs")])
        if code:
            raise RuntimeError("Unchanged traces must pass before mutation checks")
        normal = json.loads(observed.read_text(encoding="utf-8"))
        for path in HERE.glob("*.mjs"):
            shutil.copyfile(path, temporary / path.name)
        original = (HERE / "machine.mjs").read_text(encoding="utf-8")
        mutations = [
            ("cancel incorrectly commits", 'CANCEL: "idle",',
             'CANCEL: { target: "idle", actions: assign({ saved: ({ context }) => context.draft }) },',
             "01-cancel.json", 4, "state.context.saved"),
            ("blank draft can save", "guard: ({ context }) => context.draft.trim().length > 0,",
             "guard: () => true,", "02-validation.json", 3, "state.can_save"),
            ("save loses text", "actions: assign({ saved: ({ context }) => context.draft }),",
             'actions: assign({ saved: "lost" }),', "03-restore.json", 7, "state.context.saved"),
        ]
        mutation_results = []
        for name, before, after, scenario, step, field in mutations:
            if original.count(before) != 1:
                raise RuntimeError(f"Mutation anchor is ambiguous: {name}")
            (temporary / "machine.mjs").write_text(original.replace(before, after), encoding="utf-8")
            native_result, _ = run([node, "--test", str(temporary / "native.test.mjs")])
            code = main(["--trace", "--report", str(observed), str(HERE / "scenarios" / scenario),
                         "--", node, str(temporary / "main.mjs")])
            result = json.loads(observed.read_text(encoding="utf-8"))["results"][0]
            # An import error/crash is not evidence of detecting the intended defect.
            if (native_result.returncode != 1 or "ERR_ASSERTION" not in native_result.stdout
                    or code != 1 or result["passed"] or not result.get("trace")
                    or result["trace"][-1]["step"] != step
                    or not any(field in difference for difference in result["trace"][-1]["differences"])):
                raise RuntimeError(f"Did not detect the intended mutation: {name}\n{native_result.stdout}")
            mutation_results.append({"mutation": name, "native_assertion_failed": True,
                                     "trace_failure": result})
        timing = None
        if args.samples:
            # Warm caches only. Every measured command starts fresh processes. Alternate
            # order to reduce drift; exclude warm-ups, installs and JSON report writing.
            for command in [native, replay] * 3:
                result, _ = run(command)
                if result.returncode:
                    raise RuntimeError(result.stdout + result.stderr)
            samples = {"native": [], "replay": []}
            for i in range(args.samples):
                for label in (["native", "replay"] if i % 2 == 0 else ["replay", "native"]):
                    result, elapsed = run(native if label == "native" else replay)
                    if result.returncode:
                        raise RuntimeError(result.stdout + result.stderr)
                    samples[label].append(elapsed)
            timing = {name: measure(values) for name, values in samples.items()}
        for result in normal["results"]:
            result["source"] = str(Path(result["source"]).relative_to(ROOT)).replace("\\", "/")
        for mutation in mutation_results:
            result = mutation["trace_failure"]
            result["source"] = str(Path(result["source"]).relative_to(ROOT)).replace("\\", "/")
        baseline = json.loads((ROOT / "docs/evidence/xstate-install-baseline.json").read_text())
        lock = HERE / "package-lock.json"
        evidence = {
            "runner_version": VERSION,
            "environment": {"system": platform.system(), "release": platform.release(),
                            "machine": platform.machine(), "python": platform.python_version(),
                            "node": run([node, "--version"])[0].stdout.strip()},
            "install": {"baseline": baseline, "focused_non_root_entries": len(json.loads(lock.read_text())["packages"]) - 1,
                        "focused_lock_bytes": lock.stat().st_size},
            "source_files": files_stats([HERE / name for name in
                ["machine.mjs", "native.test.mjs", "adapter.mjs", "main.mjs", "protocol.mjs"]] + scenarios + [ROOT / "interaction_check.py"]),
            "replay": normal["results"], "controlled_mutations": mutation_results,
            "timing": timing,
        }
        write_report(args.report, json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
        print(f"Evidence written: {args.report}")


if __name__ == "__main__":
    verify()
