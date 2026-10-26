"""Observe Pydantic's validated field assignment on an original model."""
from pydantic import BaseModel,ConfigDict,Field,ValidationError
from python_protocol import fields
from .helpers import mapping

class Profile(BaseModel):
    """A small editing fixture with native conversion and field constraints."""
    model_config=ConfigDict(validate_assignment=True,extra="forbid",str_strip_whitespace=True)
    name:str=Field(min_length=1)
    count:int=Field(ge=0)
    enabled:bool=True

class Consumer:
    """Retain the real instance across assignments and failed replacements."""
    def __init__(self):self.model=Profile(name="Ada",count=1)
    def step(self,event):
        op=event.get("op");paths=[]
        if op=="new":
            fields(event,("op","data"));data=mapping(event["data"])
            try:self.model=Profile.model_validate(data)
            except ValidationError as exc:paths=[".".join(map(str,e["loc"])) for e in exc.errors()]
        elif op=="assign":
            fields(event,("op","field","value"))
            if event["field"] not in ("name","count","enabled"):raise ValueError("unsupported field")
            try:setattr(self.model,event["field"],event["value"])
            except ValidationError as exc:paths=[".".join(map(str,e["loc"])) for e in exc.errors()]
        else:raise ValueError("unsupported event")
        return {"value":self.model.model_dump(),"valid":not paths,"paths":sorted(paths)}
