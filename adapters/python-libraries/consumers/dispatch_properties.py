"""Drive python-dispatch properties with coalescing emission locks."""
from contextlib import nullcontext
from pydispatch import Dispatcher,Property
from python_protocol import fields
from .helpers import values
class Model(Dispatcher):
    """A numeric property with one explicitly retained receiver."""
    count=Property(0)
class Consumer:
    """Avoid any assertion about unspecified multi-listener ordering."""
    def __init__(self):self.model=Model();self.log=[];self.model.bind(count=self.receive)
    def receive(self,instance,value,**kwargs):
        """Capture the native property notification."""
        self.log.append(value)
    def step(self,event):
        op=event.get("op")
        if op=="write":
            fields(event,("op","values","locked"));batch=values(event["values"])
            if type(event["locked"]) is not bool:raise ValueError("locked must be boolean")
            with self.model.emission_lock("count") if event["locked"] else nullcontext():
                for value in batch:self.model.count=value
        elif op=="unbind":
            fields(event,("op",));self.model.unbind(self.receive)
        else:raise ValueError("unsupported event")
        return {"count":self.model.count,"log":list(self.log)}
