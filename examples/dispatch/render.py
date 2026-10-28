"""Optional, adapter-specific Markdown/Mermaid view of --trace JSON.

Not a generic event visualizer: only complete integer count/log snapshots from
this fresh Probe are supported. Intra-step callback timing is not recorded.
"""
import argparse
import json
from pathlib import Path


def integers(value):
    return (isinstance(value, list) and len(value) <= 1000
            and all(type(v) is int and abs(v) <= 1_000_000 for v in value))


def rows(result, side):
    trace = result.get("trace")
    if not isinstance(trace, list) or not 1 <= len(trace) <= 100:
        raise ValueError("need 1..100 checked steps from --trace")
    previous = []  # This adapter always starts with an empty callback log.
    output = []
    for index, entry in enumerate(trace, 1):
        state, event = entry.get(side, {}), entry.get("event", {})
        log, count = state.get("log"), state.get("count")
        if (entry.get("step") != index or type(entry.get("passed")) is not bool
                or type(count) is not int or abs(count) > 1_000_000 or not integers(log)
                or log[:len(previous)] != previous):
            raise ValueError("need consecutive steps and complete append-only count/log snapshots")
        if event == {"op": "unbind"}:
            action = "unbind receiver"
        elif (set(event) == {"op", "values", "locked"} and event["op"] == "write"
              and integers(event["values"]) and 1 <= len(event["values"]) <= 100
              and type(event["locked"]) is bool):
            action = f"writes {event['values']}; lock {'on' if event['locked'] else 'off'}"
        else:
            raise ValueError("unsupported adapter event")
        output.append((index, action, log[len(previous):], log, count, entry["passed"]))
        previous = log
    return output


def render(result):
    # All labels below are fixed strings or validated integers. Report names,
    # paths, stderr and arbitrary JSON strings never enter Mermaid source.
    lines = ["# Property notification trace", "",
             "Only checked steps are shown; the adapter may have executed the full batch.",
             "Writes are requested assignments. Callbacks are the new suffix of the cumulative log.",
             "`count` is the property value, **not** the number of callbacks.",
             "The diagrams summarize each step; they do not assert intra-step timing.", ""]
    for side, title in [("expect", "Expected"), ("actual", "Observed")]:
        data = rows(result, side)
        lines += [f"## {title}", "", "| Step | Requested action | New callbacks | Cumulative log | Property count | Check |",
                  "| --- | --- | --- | --- | --- | --- |"]
        for i, action, delta, log, count, passed in data:
            lines.append(f"| {i} | {action} | {delta} | {log} | {count} | {'pass' if passed else 'mismatch'} |")
        lines += ["", "```mermaid", "sequenceDiagram", "    participant A as Adapter",
                  "    participant M as Property count", "    participant L as Callback log"]
        for i, action, delta, log, count, passed in data:
            # Semicolons separate Mermaid statements; replace our label delimiter.
            lines += [f"    Note over A,L: Step {i} - {'pass' if passed else 'MISMATCH'}",
                      f"    A->>M: {action.replace(';', ',')}",
                      f"    Note over M,L: Callbacks during step = {delta}",
                      f"    Note over M,L: Property count = {count}, cumulative log = {log}"]
        lines += ["```", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("--result", type=int, default=0, help="zero-based result index")
    args = parser.parse_args()
    if args.report.stat().st_size > 1_048_576:
        parser.error("report exceeds 1 MiB")
    try:
        report = json.loads(args.report.read_text(encoding="utf-8"))
        if args.result < 0:
            raise ValueError("negative result index")
        print(render(report["results"][args.result]))
    except (ValueError, KeyError, IndexError, TypeError, AttributeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
