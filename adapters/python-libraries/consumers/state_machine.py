"""Drive an original synchronous Python StateMachine editing fixture."""

from python_protocol import fields, text
from statemachine import State, StateMachine
from statemachine.exceptions import TransitionNotAllowed


class Draft(StateMachine):
    """Native transitions and guards around a two-state original draft model."""

    idle = State(initial=True)
    editing = State()
    edit = idle.to(editing, before="begin")
    change = editing.to.itself(internal=True, on="replace")
    save = editing.to(idle, cond="valid", before="commit")
    cancel = editing.to(idle, before="begin")

    def __init__(self):
        self.saved = "A"
        self.draft = "A"
        super().__init__()

    def begin(self):
        """Restore the original fixture's saved text."""
        self.draft = self.saved

    def replace(self, value):
        """Only an accepted editing transition reaches this callback."""
        self.draft = value

    def valid(self):
        """Reject a blank draft through the library's own guard processing."""
        return bool(self.draft.strip())

    def commit(self):
        """Commit only after native guard acceptance."""
        self.saved = self.draft


class Consumer:
    """Expose settled native state after each synchronous send."""

    def __init__(self):
        self.machine = Draft()

    def step(self, event):
        op = event.get("op")
        rejected = False
        if op == "change":
            fields(event, ("op", "value"))
            kwargs = {"value": text(event["value"])}
        elif op in ("edit", "save", "cancel"):
            fields(event, ("op",))
            kwargs = {}
        else:
            raise ValueError("unsupported event")
        try:
            self.machine.send(op, **kwargs)
        except TransitionNotAllowed:
            rejected = True
        return {
            "state": self.machine.current_state.id,
            "draft": self.machine.draft,
            "saved": self.machine.saved,
            "rejected": rejected,
        }
