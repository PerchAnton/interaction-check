"""Small bounded JSONL transport shared by the Python consumer examples."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from interaction_check import strict_json, validate_json

LIMIT = 65536


def fields(value, required):
    if not isinstance(value, dict) or set(value) != set(required):
        raise ValueError("missing or unsupported fields")


def text(value):
    if not isinstance(value, str) or len(value) > 4096:
        raise ValueError("expected bounded text")
    value.encode("utf-8", errors="strict")
    return value


def integer(value, maximum=16384):
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError("expected bounded nonnegative integer")
    return value


def serve(step, source=None, target=None):
    source = sys.stdin.buffer if source is None else source
    target = sys.stdout.buffer if target is None else target
    count = 0
    while line := source.readline(LIMIT + 1):
        count += 1
        if len(line) > LIMIT or count > 1024:
            raise ValueError("request limit exceeded")
        packet = strict_json(line.decode("utf-8", errors="strict"))
        fields(packet, ("protocol", "id", "event"))
        if type(packet["protocol"]) is not int or packet["protocol"] != 1:
            raise ValueError("unsupported protocol")
        integer(packet["id"], 2**53 - 1)
        if not isinstance(packet["event"], dict):
            raise ValueError("expected event object")
        state = step(packet["event"])
        if not isinstance(state, dict):
            raise ValueError("expected state object")
        validate_json(state)
        response = json.dumps({"protocol": 1, "id": packet["id"], "state": state},
                              ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n"
        if len(response) > LIMIT:
            raise ValueError("response limit exceeded")
        target.write(response)
        target.flush()
