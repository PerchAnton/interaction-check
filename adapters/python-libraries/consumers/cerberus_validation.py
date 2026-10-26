"""Expose Cerberus normalized documents even when validation fails."""
from cerberus import Validator
from python_protocol import fields
from .helpers import mapping,parsed

class Consumer:
    """Reuse a native Validator to exercise error-state recovery."""
    def __init__(self):
        self.validator=Validator({"name":{"type":"string","required":True,"minlength":1,"coerce":str.strip},"count":{"type":"integer","required":True,"min":0,"coerce":int},"enabled":{"type":"boolean","default":True}},purge_unknown=True)
    def step(self,event):
        fields(event,("op","data"))
        if event["op"]!="validate":raise ValueError("unsupported event")
        work=mapping(event["data"]);valid=self.validator.validate(work)
        return parsed(valid,self.validator.document,list(self.validator.errors),event["data"],work)
