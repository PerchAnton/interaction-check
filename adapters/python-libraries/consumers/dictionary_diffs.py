"""Replay native Dictdiffer patch and revert operations on JSON objects."""

from copy import deepcopy

from dictdiffer import diff, patch, revert
from python_protocol import fields

from .helpers import mapping


class Consumer:
    """Store a native diff, keeping the old snapshot available for comparison."""

    def __init__(self):
        self.document = {}
        self.changes = []
        self.original = {}

    def step(self, event):
        op = event.get("op")
        if op == "new":
            fields(event, ("op", "data"))
            self.document = mapping(event["data"])
            self.original = deepcopy(self.document)
            self.changes = []
        elif op == "plan":
            fields(event, ("op", "target"))
            target = mapping(event["target"])
            self.changes = list(diff(self.document, target))
        elif op == "apply":
            fields(event, ("op",))
            self.document = patch(self.changes, self.document)
        elif op == "revert":
            fields(event, ("op",))
            self.document = revert(self.changes, self.document)
        else:
            raise ValueError("unsupported event")
        return {
            "document": deepcopy(self.document),
            "original": deepcopy(self.original),
            "changes": len(self.changes),
        }
