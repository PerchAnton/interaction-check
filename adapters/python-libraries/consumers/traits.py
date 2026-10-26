"""Observe held Traitlets notifications, validation and observer removal."""
from contextlib import nullcontext
from traitlets import HasTraits,Int,Unicode,TraitError
from python_protocol import fields
from .helpers import updates
class Model(HasTraits):
    """Original bounded form fields."""
    count=Int(default_value=0,min=0,max=10)
    label=Unicode(default_value="A")
class Consumer:
    """Use native hold_trait_notifications; do not simulate rollback."""
    def __init__(self):
        self.model=Model();self.log=[];self.model.observe(self.receive,names=["count","label"])
    def receive(self,e):
        """Record an actual change event."""
        self.log.append({"field":e.name,"old":e.old,"new":e.new})
    def step(self,event):
        op=event.get("op");error=False
        if op=="write":
            fields(event,("op","hold","updates"));batch=updates(event["updates"])
            if type(event["hold"]) is not bool:raise ValueError("hold must be boolean")
            try:
                with self.model.hold_trait_notifications() if event["hold"] else nullcontext():
                    for name,value in batch:setattr(self.model,name,value)
            except TraitError:error=True
        elif op=="unwatch":
            fields(event,("op",));self.model.unobserve(self.receive,names=["count","label"])
        else:raise ValueError("unsupported event")
        return {"count":self.model.count,"label":self.model.label,"log":list(self.log),"rejected":error}
