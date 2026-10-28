from pathlib import Path
import sys
import os

# Do not load or update a user's napari settings. Built-in icon cache remains native.
os.environ["NAPARI_CONFIG"] = ""

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from python_protocol import fields, text, serve
import numpy as np
from napari.components import LayerList
from napari.layers import Image


def fixture():
    return LayerList([Image(np.zeros((2, 2), dtype=np.uint8), name="a"),
                      Image(np.ones((2, 2), dtype=np.uint8), name="b")])


class Adapter:
    def __init__(self):
        self.layers = None

    def step(self, event):
        op = event.get("op")
        if op == "new":
            fields(event, ["op"])
            self.layers = fixture()
            self.layers.selection.clear()
        else:
            if self.layers is None:
                raise ValueError("new must be first")
            if op == "select":
                fields(event, ["op", "name"])
                self.layers.selection.add(self.layers[text(event["name"])])
            elif op == "lock":
                fields(event, ["op", "name", "locked"])
                if type(event["locked"]) is not bool:
                    raise ValueError("expected boolean")
                self.layers[text(event["name"])].locked = event["locked"]
            elif op == "remove_selected":
                fields(event, ["op"])
                self.layers.remove_selected()
            elif op == "toggle_visibility":
                fields(event, ["op"])
                self.layers.toggle_selected_visibility()
            else:
                raise ValueError("unsupported operation")
        return {"layers": [{"name": layer.name, "locked": bool(layer.locked), "visible": layer.visible}
                           for layer in self.layers],
                "selected": sorted(layer.name for layer in self.layers.selection)}


if __name__ == "__main__":
    adapter = Adapter()
    serve(adapter.step)
