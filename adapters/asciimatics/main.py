"""Exercise native asciimatics Text validation and editing, without a Screen."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen
from asciimatics.widgets import Text
from python_protocol import fields, serve, text

widget = None
changes = 0


def changed():
    """Count the widget's own change callbacks."""
    global changes
    changes += 1


def step(event):
    """Dispatch native keyboard events and expose public value/validity."""
    global widget, changes
    op = event.get("op")
    if op == "new":
        fields(event, ("op", "text"), ("max_length", "readonly", "digits_only"))
        maximum = event.get("max_length")
        if maximum is not None and (
            type(maximum) is not int or not 1 <= maximum <= 4096
        ):
            raise ValueError("invalid max_length")
        widget = Text(
            on_change=changed,
            max_length=maximum,
            readonly=event.get("readonly", False),
            validator=str.isdecimal if event.get("digits_only", False) else None,
        )
        widget.value = text(event["text"])
        changes = 0
    elif widget is None:
        raise ValueError("first event must be new")
    elif op == "text":
        fields(event, ("op", "text"))
        for char in text(event["text"]):
            widget.process_event(KeyboardEvent(ord(char)))
    elif op == "key":
        fields(event, ("op", "key"))
        keys = {
            "left": Screen.KEY_LEFT,
            "right": Screen.KEY_RIGHT,
            "home": Screen.KEY_HOME,
            "end": Screen.KEY_END,
            "backspace": Screen.KEY_BACK,
            "delete": Screen.KEY_DELETE,
        }
        if event["key"] not in keys:
            raise ValueError("unsupported key")
        widget.process_event(KeyboardEvent(keys[event["key"]]))
    else:
        raise ValueError("unsupported event")
    return {"value": widget.value, "valid": widget.is_valid, "changes": changes}


if __name__ == "__main__":
    serve(step)
