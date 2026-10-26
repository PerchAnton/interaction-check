"""Observe Glom path assignment, deletion and missing-path recovery."""

from copy import deepcopy

from glom import Assign, Delete, GlomError, Path, glom
from python_protocol import fields, text

from .helpers import mapping


class Consumer:
    """Only literal path segments and values are accepted; no executable specs."""

    def __init__(self):
        self.document = {}

    def step(self, event):
        op = event.get("op")
        value = None
        error = None
        if op == "new":
            fields(event, ("op", "data"))
            self.document = mapping(event["data"])
        elif op in ("assign", "delete", "get"):
            fields(event, ("op", "path", "value") if op == "assign" else ("op", "path"))
            parts = event["path"]
            if not isinstance(parts, list) or not 1 <= len(parts) <= 12:
                raise ValueError("path must have 1..12 string segments")
            path = Path(*(text(p) for p in parts))
            try:
                if op == "assign":
                    glom(
                        self.document,
                        Assign(path, deepcopy(event["value"]), missing=dict),
                    )
                elif op == "delete":
                    glom(self.document, Delete(path))
                else:
                    value = glom(self.document, path)
            except GlomError as exc:
                error = type(exc).__name__
        else:
            raise ValueError("unsupported event")
        return {
            "document": deepcopy(self.document),
            "value": deepcopy(value),
            "error": error,
        }
