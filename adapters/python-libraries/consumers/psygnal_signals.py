"""Observe native signal blocking, pausing and queued-event reduction."""

from contextlib import nullcontext

from psygnal import Signal
from python_protocol import fields

from .helpers import values


class Emitter:
    """A typed signal independent of Qt and a graphical event loop."""

    changed = Signal(int)


class Consumer:
    """Capture actual delivered arguments after context exit."""

    def __init__(self):
        self.emitter = Emitter()
        self.log = []
        self.emitter.changed.connect(self.receive)

    def receive(self, value):
        """Record the callback argument."""
        self.log.append(value)

    def step(self, event):
        op = event.get("op")
        during = None
        if op == "emit":
            fields(event, ("op", "values", "mode"))
            batch = values(event["values"])
            signal = self.emitter.changed
            modes = {
                "plain": nullcontext,
                "blocked": signal.blocked,
                "paused": signal.paused,
                "last": lambda: signal.paused(lambda a, b: b),
            }
            if event["mode"] not in modes:
                raise ValueError("unsupported mode")
            with modes[event["mode"]]():
                for value in batch:
                    signal.emit(value)
                during = len(self.log)
        elif op == "disconnect":
            fields(event, ("op",))
            self.emitter.changed.disconnect(self.receive)
        else:
            raise ValueError("unsupported event")
        return {
            "log": list(self.log),
            "listeners": len(self.emitter.changed),
            "during": during,
        }
