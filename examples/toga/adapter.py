import os
from pathlib import Path
import sys

os.environ["TOGA_BACKEND"] = "toga_dummy"
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from python_protocol import fields, integer, text, serve
import toga


class Adapter:
    def __init__(self):
        self.selection = None
        self.changes = 0

    def changed(self, *_args, **_kwargs):
        self.changes += 1

    def step(self, event):
        op = event.get("op")
        if op == "new":
            fields(event, ["op"])
            self.selection = toga.Selection(items=["a", "b"], on_change=self.changed)
            self.changes = 0
        else:
            if self.selection is None:
                raise ValueError("new must be first")
            if op == "select":
                fields(event, ["op", "value"])
                self.selection.value = text(event["value"])
            elif op == "remove":
                fields(event, ["op", "index"])
                i = integer(event["index"])
                if i >= len(self.selection.items):
                    raise ValueError("item out of range")
                self.selection.items.remove(self.selection.items[i])
            elif op == "clear":
                fields(event, ["op"])
                self.selection.items.clear()
            elif op == "append":
                fields(event, ["op", "value"])
                self.selection.items.append(text(event["value"]))
            else:
                raise ValueError("unsupported operation")
        return {"items": [row.value for row in self.selection.items],
                "value": self.selection.value, "changes": self.changes}


if __name__ == "__main__":
    adapter = Adapter()
    serve(adapter.step)
