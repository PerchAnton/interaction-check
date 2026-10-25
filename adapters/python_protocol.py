"""Bounded JSONL transport for external Python widget adapters."""

import json
import sys


def read_request():
    """Read one strict protocol envelope, or return None at EOF."""
    line = sys.stdin.buffer.readline(65537)
    if not line:
        return None
    if len(line) > 65536:
        raise ValueError("request exceeds 64 KiB")
    request = json.loads(line)
    if not isinstance(request, dict) or set(request) != {"protocol", "id", "event"}:
        raise ValueError("expected protocol, id and event only")
    if type(request["protocol"]) is not int or request["protocol"] != 1:
        raise ValueError("unsupported protocol")
    if type(request["id"]) is not int or request["id"] < 0:
        raise ValueError("id must be a non-negative integer")
    if not isinstance(request["event"], dict):
        raise ValueError("event must be an object")
    return request


def emit(request, state):
    """Return observed state with the exact request identifier."""
    print(json.dumps({"protocol": 1, "id": request["id"], "state": state}), flush=True)


def fields(event, required, optional=()):
    """Reject missing or unknown event fields."""
    if set(event) - set(required) - set(optional) or set(required) - set(event):
        raise ValueError("invalid event fields")
    for name in ("digits_only", "multiline", "readonly"):
        if name in event and type(event[name]) is not bool:
            raise ValueError(f"{name} must be boolean")


def text(value):
    """Bound synthetic text before calling the native widget."""
    if not isinstance(value, str) or len(value) > 4096:
        raise ValueError("text must be a string of at most 4096 codepoints")
    return value


def width(value):
    """Keep renderer dimensions bounded and nonzero."""
    if type(value) is not int or not 2 <= value <= 200:
        raise ValueError("width must be between 2 and 200")
    return value


def serve(step):
    """Run the synchronous adapter until EOF; errors fail the process."""
    while (request := read_request()) is not None:
        emit(request, step(request["event"]))
