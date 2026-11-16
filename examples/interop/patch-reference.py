"""Real jsonpatch application in copy mode; adapter expectations are never received."""
import json
import sys
from copy import deepcopy
from jsonpatch import JsonPatch, JsonPatchException
from jsonpointer import JsonPointerException


def validate_patch(patch):
    if not isinstance(patch, list) or len(patch) > 64:
        raise ValueError("at most 64 operations")
    for item in patch:
        op = item.get("op") if isinstance(item, dict) else None
        fields = {"op", "path", "value"} if op in ("add", "replace") else (
            {"op", "path", "from"} if op in ("move", "copy") else {"op", "path"} if op == "remove" else set())
        if not fields or set(item) != fields:
            raise ValueError("unsupported operation")
        for key in ("path", "from"):
            if key not in item:
                continue
            value = item[key]
            if not isinstance(value, str) or not value.startswith("/") or len(value) > 4096:
                raise ValueError("non-root pointer required")
            import re
            if re.search(r"~(?:[^01]|$)", value):
                raise ValueError("invalid escape")
            if any(part.replace("~1", "/").replace("~0", "~") in ("__proto__", "prototype", "constructor")
                   for part in value[1:].split("/")):
                raise ValueError("reserved path")


class Reference:
    def __init__(self):
        self.document = {}

    def step(self, event):
        error = None
        if event.get("op") == "new" and set(event) == {"op", "data"}:
            if not isinstance(event["data"], dict):
                raise ValueError("object required")
            self.document = deepcopy(event["data"])
        elif event.get("op") == "apply" and set(event) == {"op", "patch"}:
            try:
                validate_patch(event["patch"])
                self.document = JsonPatch(event["patch"]).apply(self.document, in_place=False)
            except (ValueError, TypeError, KeyError, JsonPatchException, JsonPointerException):
                error = "rejected"
        else:
            raise ValueError("unsupported event")
        return {"document": deepcopy(self.document), "error": error}


if __name__ == "__main__":
    adapter = Reference()
    while line := sys.stdin.buffer.readline(65537):
        if len(line) > 65536:
            raise ValueError("request exceeds 64 KiB")
        request = json.loads(line)
        if set(request) != {"protocol", "id", "event"} or type(request["protocol"]) is not int or request["protocol"] != 1:
            raise ValueError("invalid request")
        if type(request["id"]) is not int or request["id"] < 0 or not isinstance(request["event"], dict):
            raise ValueError("invalid request")
        print(json.dumps({"protocol": 1, "id": request["id"], "state": adapter.step(request["event"])}), flush=True)
