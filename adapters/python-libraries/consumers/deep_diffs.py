"""Use DeepDiff's native bidirectional Delta without loading serialized data."""

from copy import deepcopy

from deepdiff import DeepDiff, Delta
from python_protocol import fields

from .helpers import mapping


class Consumer:
    """Observe native apply/subtract on small original JSON documents."""

    def __init__(self):
        self.document = {}
        self.original = {}
        self.delta = None
        self.kinds = []

    def step(self, event):
        op = event.get("op")
        if op == "new":
            fields(event, ("op", "data"))
            self.document = mapping(event["data"])
            self.original = deepcopy(self.document)
            self.delta = None
            self.kinds = []
        elif op == "plan":
            fields(event, ("op", "target"))
            target = mapping(event["target"])
            difference = DeepDiff(self.document, target)
            self.delta = Delta(difference, bidirectional=True, raise_errors=True)
            self.kinds = sorted(difference)
        elif op in ("apply", "revert"):
            fields(event, ("op",))
            if self.delta is None:
                raise ValueError("plan a delta first")
            self.document = (
                self.document + self.delta
                if op == "apply"
                else self.document - self.delta
            )
        else:
            raise ValueError("unsupported event")
        return {
            "document": deepcopy(self.document),
            "original": deepcopy(self.original),
            "kinds": list(self.kinds),
        }
