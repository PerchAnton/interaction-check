"""Render only checked event observations; never infer callbacks from a value change."""
import json
from pathlib import Path
import sys


def render(report):
    lines = ["# Event observations", "", "Only checked steps are drawn. Later adapter events may already have executed.", ""]
    for result in report["results"]:
        rows = result.get("trace")
        if not rows:
            raise ValueError("rerun with --trace")
        lines += ["| Step | Operation | Expected writes / callbacks / log | Observed writes / callbacks / log | Match |",
                  "| --- | --- | --- | --- | --- |"]
        diagram = ["```mermaid", "sequenceDiagram", "    participant R as Runner", "    participant A as Adapter"]
        for row in rows:
            op = row["event"]["op"]
            if op not in ("new", "on", "write", "emit"):
                raise ValueError("not an event trace")
            counts = []
            for state in (row["expect"], row["actual"]):
                if type(state.get("writes")) is not int or not isinstance(state.get("callbacks"), list) or not isinstance(state.get("log"), list):
                    raise ValueError("explicit write/callback/log observations required")
                counts.append((state["writes"], len(state["callbacks"]), len(state["log"])))
            step = row["step"]
            if type(step) is not int or step < 1:
                raise ValueError("invalid step")
            lines.append(f"| {step} | {op} | {' / '.join(map(str, counts[0]))} | {' / '.join(map(str, counts[1]))} | {'pass' if row['passed'] else 'FAIL'} |")
            diagram += [f"    R->>A: Step {step} ({op})", f"    Note over R,A: expected {counts[0][1]} callbacks; observed {counts[1][1]}"]
        lines += ["", *diagram, "```", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    print(render(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))))
