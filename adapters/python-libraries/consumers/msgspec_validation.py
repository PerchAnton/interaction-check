"""Exercise typed msgspec conversion; no assignment-validation claim."""
from typing import Annotated
import msgspec
from python_protocol import fields
from .helpers import mapping,parsed

class Profile(msgspec.Struct,forbid_unknown_fields=True):
    """Original fixed Struct, not an arbitrary schema evaluator."""
    name:Annotated[str,msgspec.Meta(min_length=1)]
    count:Annotated[int,msgspec.Meta(ge=0)]
    enabled:bool=True

class Consumer:
    """Report native conversion rejection without matching error prose."""
    def step(self,event):
        fields(event,("op","data","strict"))
        if event["op"]!="validate" or type(event["strict"]) is not bool:raise ValueError("expected validate with boolean strict")
        work=mapping(event["data"])
        try:return parsed(True,msgspec.to_builtins(msgspec.convert(work,type=Profile,strict=event["strict"])),[],event["data"],work)
        except msgspec.ValidationError:return parsed(False,None,[],event["data"],work)
