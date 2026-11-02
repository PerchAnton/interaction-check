"""Replay copy and in-place operations against the installed jsonpatch library."""

from copy import deepcopy
import json
import sys

from jsonpatch import JsonPatch, JsonPatchException
from jsonpointer import JsonPointerException


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


def fields(event, required):
    if event.keys() != set(required):
        raise ValueError("invalid event fields")


def mapping(value):
    """Isolate a bounded request object before passing it to native code."""
    if not isinstance(value, dict) or len(value) > 100:
        raise ValueError("expected object with at most 100 fields")
    return deepcopy(value)


class Consumer:
    """Observe native patch effects; never invent transactional rollback."""

    def __init__(self):
        self.document = {}

    def step(self, event):
        op = event.get("op")
        error = None
        if op == "new":
            fields(event, ("op", "data"))
            self.document = mapping(event["data"])
        elif op == "apply":
            fields(event, ("op", "patch", "in_place"))
            if (
                type(event["in_place"]) is not bool
                or not isinstance(event["patch"], list)
                or len(event["patch"]) > 64
            ):
                raise ValueError("invalid patch arguments")
            patch = deepcopy(event["patch"])
            try:
                self.document = JsonPatch(patch).apply(
                    self.document, in_place=event["in_place"]
                )
            except (JsonPatchException, JsonPointerException) as exc:
                error = type(exc).__name__
        else:
            raise ValueError("unsupported event")
        return {"document": deepcopy(self.document), "error": error}


if __name__ == "__main__":
    consumer = Consumer()
    while (request := read_request()) is not None:
        state = consumer.step(request["event"])
        print(json.dumps({"protocol": 1, "id": request["id"], "state": state}), flush=True)
