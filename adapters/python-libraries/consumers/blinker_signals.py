"""Exercise sender-specific Blinker connections and muted sends."""

from contextlib import nullcontext

from blinker import Signal
from python_protocol import fields

from .helpers import integer


class Consumer:
    """Retain the receiver explicitly without GC timing assumptions."""

    def __init__(self):
        self.signal = Signal()
        self.log = []

    def receive(self, sender, value):
        """Capture native send arguments and return the supplied value."""
        self.log.append({"sender": sender, "value": value})
        return value

    def step(self, event):
        op = event.get("op")
        delivered = None
        if op in ("connect", "disconnect"):
            fields(event, ("op", "sender"))
            if event["sender"] not in ("left", "right"):
                raise ValueError("unsupported sender")
            if op == "connect":
                self.signal.connect(self.receive, sender=event["sender"], weak=False)
            else:
                self.signal.disconnect(self.receive, sender=event["sender"])
        elif op == "send":
            fields(event, ("op", "sender", "value", "muted"))
            value = integer(event["value"])
            if (
                event["sender"] not in ("left", "right")
                or type(event["muted"]) is not bool
            ):
                raise ValueError("invalid send")
            with self.signal.muted() if event["muted"] else nullcontext():
                delivered = len(self.signal.send(event["sender"], value=value))
        else:
            raise ValueError("unsupported event")
        return {"log": list(self.log), "delivered": delivered}
