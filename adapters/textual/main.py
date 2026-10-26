"""Replay Input events through a real headless Textual App and Pilot."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from python_protocol import emit, fields, read_request, text, width
from textual.app import App, ComposeResult
from textual.widgets import Input


class Probe(App):
    """Minimal application whose native Input is the system under test."""

    def __init__(self, value, restrict):
        super().__init__()
        self.initial_value = value
        self.restrict = restrict

    def compose(self) -> ComposeResult:
        """Create one focusable native input without select-on-focus."""
        yield Input(self.initial_value, restrict=self.restrict, select_on_focus=False)


def state(widget):
    """Read public widget state after the event loop settles."""
    return {
        "value": widget.value,
        "cursor_codepoints": widget.cursor_position,
        "focused": widget.has_focus,
    }


async def main():
    """Keep one app alive per scenario and wait for each Pilot action."""
    request = read_request()
    if request is None:
        return
    event = request["event"]
    fields(event, ("op", "text", "width"), ("digits_only",))
    if event["op"] != "new":
        raise ValueError("first event must be new")
    app = Probe(
        text(event["text"]), r"[0-9]*" if event.get("digits_only", False) else None
    )
    async with app.run_test(size=(width(event["width"]), 10)) as pilot:
        widget = app.query_one(Input)
        await pilot.pause()
        emit(request, state(widget))
        while (request := await asyncio.to_thread(read_request)) is not None:
            event = request["event"]
            if event.get("op") == "text":
                fields(event, ("op", "text"))
                await pilot.press(*text(event["text"]))
            elif event.get("op") == "key":
                fields(event, ("op", "key"))
                if event["key"] not in (
                    "left",
                    "right",
                    "home",
                    "end",
                    "backspace",
                    "delete",
                ):
                    raise ValueError("unsupported key")
                await pilot.press(event["key"])
            elif event.get("op") == "resize":
                fields(event, ("op", "width"))
                await pilot.resize_terminal(width(event["width"]), 10)
            else:
                raise ValueError("unsupported event")
            await pilot.pause()
            emit(request, state(widget))


if __name__ == "__main__":
    asyncio.run(main())
