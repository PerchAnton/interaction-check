"""Observe native prompt_toolkit Buffer editing without a terminal."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator
from python_protocol import fields, serve, text

buffer = None


def step(event):
    """Dispatch a single native buffer operation and read its state."""
    global buffer
    op = event.get("op")
    if op == "new":
        fields(event, ("op", "text"), ("digits_only",))
        value = text(event["text"])
        validator = (
            Validator.from_callable(str.isdecimal, error_message="digits required")
            if event.get("digits_only", False)
            else None
        )
        buffer = Buffer(document=Document(value, len(value)), validator=validator)
    elif buffer is None:
        raise ValueError("first event must be new")
    elif op == "text":
        fields(event, ("op", "text"))
        buffer.insert_text(text(event["text"]))
    elif op == "checkpoint":
        fields(event, ("op",))
        buffer.save_to_undo_stack()
    elif op == "validate":
        fields(event, ("op",))
        buffer.validate(set_cursor=True)
    elif op == "key":
        fields(event, ("op", "key"))
        key = event["key"]
        actions = {
            "left": buffer.cursor_left,
            "right": buffer.cursor_right,
            "backspace": buffer.delete_before_cursor,
            "delete": buffer.delete,
            "undo": buffer.undo,
            "redo": buffer.redo,
        }
        if key == "home":
            buffer.cursor_position = 0
        elif key == "end":
            buffer.cursor_position = len(buffer.text)
        elif key in actions:
            actions[key]()
        else:
            raise ValueError("unsupported key")
    else:
        raise ValueError("unsupported event")
    return {
        "value": buffer.text,
        "cursor_codepoints": buffer.cursor_position,
        "validation_error": buffer.validation_error.message
        if buffer.validation_error
        else None,
    }


if __name__ == "__main__":
    serve(step)
