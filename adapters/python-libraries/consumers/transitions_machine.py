"""Drive an original edit/cancel machine through transitions' native guards."""

from python_protocol import fields, text
from transitions import Machine, MachineError


class Consumer:
    """The library routes transitions; callbacks define only this draft fixture."""

    def __init__(self):
        self.saved = "A"
        self.draft = "A"
        self.machine = Machine(
            model=self,
            states=["idle", "editing"],
            initial="idle",
            auto_transitions=False,
            send_event=True,
        )
        self.machine.add_transition("edit", "idle", "editing", before=self.begin)
        self.machine.add_transition("change", "editing", None, before=self.replace)
        self.machine.add_transition(
            "save", "editing", "idle", conditions=self.valid, before=self.commit
        )
        self.machine.add_transition("cancel", "editing", "idle", before=self.begin)

    def begin(self, event):
        """Copy the saved fixture text into the editable draft."""
        self.draft = self.saved

    def replace(self, event):
        """Apply text only after the engine accepts the editing-state event."""
        self.draft = event.kwargs["value"]

    def valid(self, event):
        """A deliberately small original guard."""
        return bool(self.draft.strip())

    def commit(self, event):
        """Commit the fixture only when the native guard permits it."""
        self.saved = self.draft

    def step(self, event):
        op = event.get("op")
        if op == "change":
            fields(event, ("op", "value"))
            kwargs = {"value": text(event["value"])}
        elif op in ("edit", "save", "cancel"):
            fields(event, ("op",))
            kwargs = {}
        else:
            raise ValueError("unsupported event")
        try:
            rejected = not self.trigger(op, **kwargs)
        except MachineError:
            rejected = True
        return {
            "state": self.state,
            "draft": self.draft,
            "saved": self.saved,
            "rejected": rejected,
        }
