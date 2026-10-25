"""Drive the separately installed LGPL Urwid Edit through public APIs."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import urwid
from python_protocol import fields, serve, text, width

widget = None
columns = 20
unhandled = None


def step(event):
    """Send native keypresses or render at a new width, then observe Edit."""
    global widget, columns, unhandled
    op = event.get("op")
    unhandled = None
    if op == "new":
        fields(event, ("op", "text", "width"), ("multiline",))
        columns = width(event["width"])
        widget = urwid.Edit(
            edit_text=text(event["text"]), multiline=event.get("multiline", False)
        )
    elif widget is None:
        raise ValueError("first event must be new")
    elif op == "resize":
        fields(event, ("op", "width"))
        columns = width(event["width"])
    elif op == "text":
        fields(event, ("op", "text"))
        for char in text(event["text"]):
            unhandled = widget.keypress((columns,), char)
    elif op == "key":
        fields(event, ("op", "key"))
        if event["key"] not in (
            "left",
            "right",
            "home",
            "end",
            "backspace",
            "delete",
            "enter",
            "up",
            "down",
        ):
            raise ValueError("unsupported key")
        unhandled = widget.keypress((columns,), event["key"])
    else:
        raise ValueError("unsupported event")
    canvas = widget.render((columns,), focus=True)
    return {
        "value": widget.edit_text,
        "cursor_codepoints": widget.edit_pos,
        "cursor_xy": list(canvas.cursor) if canvas.cursor else None,
        "rows": canvas.rows(),
        "unhandled": unhandled,
    }


if __name__ == "__main__":
    serve(step)
