"""Observe synchronous Pyee once removal before reentrant emission."""
from pyee import EventEmitter,PyeeError
from python_protocol import fields
from .helpers import integer
class Consumer:
    """Use named original handlers, never callbacks supplied by the trace."""
    def __init__(self):
        self.emitter=EventEmitter();self.log=[];self.handlers={"ordinary":self.ordinary,"reentrant":self.reentrant}
    def ordinary(self,value):
        """Record a persistent listener call."""
        self.log.append(["ordinary",value])
    def reentrant(self,value):
        """The once handler should be gone before this nested emit."""
        self.log.append(["once",value]);self.emitter.emit("value",value+1)
    def step(self,event):
        op=event.get("op");delivered=None;error=None
        if op=="connect":
            fields(event,("op","handler"))
            if event["handler"] not in self.handlers:raise ValueError("unsupported handler")
            handler=self.handlers[event["handler"]]
            if event["handler"]=="reentrant":self.emitter.once("value",handler)
            else:self.emitter.on("value",handler)
        elif op=="remove":
            fields(event,("op",));self.emitter.remove_all_listeners("value")
        elif op=="emit":
            fields(event,("op","value"));delivered=self.emitter.emit("value",integer(event["value"]))
        elif op=="error":
            fields(event,("op",))
            try:self.emitter.emit("error","synthetic failure")
            except PyeeError as exc:error=type(exc).__name__
        else:raise ValueError("unsupported event")
        return {"log":list(self.log),"listeners":len(self.emitter.listeners("value")),"delivered":delivered,"error":error}
