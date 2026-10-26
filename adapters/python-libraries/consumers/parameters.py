"""Observe Param watcher batching, validation and event suppression."""
from contextlib import nullcontext
import param
from param.parameterized import batch_call_watchers,discard_events
from python_protocol import fields
from .helpers import updates
class Model(param.Parameterized):
    """Original bounded editing fields."""
    count=param.Integer(default=0,bounds=(0,10))
    label=param.String(default="A")
class Consumer:
    """Capture actual watcher arguments rather than simulated changes."""
    def __init__(self):
        self.model=Model();self.log=[];self.watcher=self.model.param.watch(self.receive,["count","label"])
    def receive(self,*events):
        """Preserve each native event's name, previous value and new value."""
        self.log.extend({"field":e.name,"old":e.old,"new":e.new} for e in events)
    def step(self,event):
        op=event.get("op");error=False
        if op=="write":
            fields(event,("op","mode","updates"));batch=updates(event["updates"])
            modes={"plain":nullcontext,"batch":lambda:batch_call_watchers(self.model),"discard":lambda:discard_events(self.model)}
            if event["mode"] not in modes:raise ValueError("unsupported mode")
            try:
                with modes[event["mode"]]():
                    for name,value in batch:setattr(self.model,name,value)
            except ValueError:error=True
        elif op=="unwatch":
            fields(event,("op",));self.model.param.unwatch(self.watcher)
        else:raise ValueError("unsupported event")
        return {"count":self.model.count,"label":self.model.label,"log":list(self.log),"rejected":error}
