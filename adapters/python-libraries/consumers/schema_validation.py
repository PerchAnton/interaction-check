"""Observe schema Use transformations, defaults and extra-key rejection."""
from schema import Schema,And,Use,Optional,SchemaError
from python_protocol import fields
from .helpers import mapping,parsed

class Consumer:
    """Use a fixed original schema through its public validate method."""
    def __init__(self):self.schema=Schema({"name":And(str,Use(str.strip),lambda s:len(s)>0),"count":And(Use(int),lambda n:n>=0),Optional("enabled",default=True):bool})
    def step(self,event):
        fields(event,("op","data"))
        if event["op"]!="validate":raise ValueError("unsupported event")
        work=mapping(event["data"])
        try:return parsed(True,self.schema.validate(work),[],event["data"],work)
        except SchemaError:return parsed(False,None,[],event["data"],work)
