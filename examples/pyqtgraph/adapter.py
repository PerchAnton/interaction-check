import os
from pathlib import Path
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("PYQTGRAPH_QT_LIB", "PyQt6")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from python_protocol import fields, integer, text, serve
import pyqtgraph as pg
from pyqtgraph.parametertree import Parameter


def fixture():
    return Parameter.create(name="settings", type="group", children=[
        {"name": "left", "type": "int", "value": 1},
        {"name": "right", "type": "int", "value": 2},
    ])


class Adapter:
    def __init__(self):
        self.app = pg.mkQApp("Interaction check")
        self.root = None
        self.saved = None
        self.notifications = 0

    def changed(self, *_):
        self.notifications += 1

    def step(self, event):
        op = event.get("op")
        if op == "new":
            fields(event, ["op"])
            if self.root is not None:
                self.root.sigTreeStateChanged.disconnect(self.changed)
            self.root = fixture()
            self.saved = None
            self.notifications = 0
            self.root.sigTreeStateChanged.connect(self.changed)
        else:
            if self.root is None:
                raise ValueError("new must be first")
            if op == "set":
                fields(event, ["op", "name", "value"])
                name = text(event["name"])
                if name not in ("left", "right"):
                    raise ValueError("unknown parameter")
                self.root.child(name).setValue(integer(event["value"]))
            elif op == "batch":
                fields(event, ["op", "left", "right"])
                left, right = integer(event["left"]), integer(event["right"])
                with self.root.treeChangeBlocker():
                    self.root.child("left").setValue(left)
                    self.root.child("right").setValue(right)
            elif op == "save":
                fields(event, ["op"])
                self.saved = self.root.saveState()
            elif op == "restore":
                fields(event, ["op"])
                if self.saved is None:
                    raise ValueError("save required")
                self.root.restoreState(self.saved)
            else:
                raise ValueError("unsupported operation")
        self.app.processEvents()
        return {"left": self.root.child("left").value(), "right": self.root.child("right").value(),
                "notifications": self.notifications}


if __name__ == "__main__":
    adapter = Adapter()
    serve(adapter.step)
