"""Use RxPY virtual time for deterministic debounce and disposal traces."""

from python_protocol import fields
from reactivex import operators as ops
from reactivex.subject import Subject
from reactivex.testing import TestScheduler

from .helpers import integer


class Consumer:
    """No wall-clock sleeps, background threads or network calls."""

    def __init__(self):
        self.scheduler = TestScheduler()
        self.source = Subject()
        self.log = []
        self.completed = False
        self.subscription = self.source.pipe(
            ops.debounce(10, scheduler=self.scheduler)
        ).subscribe(self.log.append, on_completed=self.complete)

    def complete(self):
        """Record the real completion callback."""
        self.completed = True

    def step(self, event):
        op = event.get("op")
        if op == "next":
            fields(event, ("op", "value"))
            self.source.on_next(integer(event["value"]))
        elif op == "advance":
            fields(event, ("op", "time"))
            time = integer(event["time"])
            if time < self.scheduler.clock:
                raise ValueError("time must not go backwards")
            self.scheduler.advance_to(time)
        elif op == "complete":
            fields(event, ("op",))
            self.source.on_completed()
        elif op == "dispose":
            fields(event, ("op",))
            self.subscription.dispose()
        else:
            raise ValueError("unsupported event")
        return {
            "time": self.scheduler.clock,
            "log": list(self.log),
            "completed": self.completed,
        }
