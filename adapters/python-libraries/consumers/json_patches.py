"""Contrast copy and in-place JSON Patch failure behavior explicitly."""

from copy import deepcopy

from jsonpatch import JsonPatch, JsonPatchException
from jsonpointer import JsonPointerException
from python_protocol import fields

from .helpers import mapping


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
