"""Check JSON Schema annotations without treating defaults as writes."""
from jsonschema import Draft202012Validator
from python_protocol import fields
from .helpers import mapping,parsed

SCHEMA={"type":"object","properties":{"name":{"type":"string","minLength":1},"count":{"type":"integer","minimum":0},"enabled":{"type":"boolean","default":True}},"required":["name","count"],"additionalProperties":False}
class Consumer:
    """Reuse a normal validator without remote references or format plugins."""
    def __init__(self):self.validator=Draft202012Validator(SCHEMA)
    def step(self,event):
        fields(event,("op","data"))
        if event["op"]!="validate":raise ValueError("unsupported event")
        work=mapping(event["data"]);errors=list(self.validator.iter_errors(work))
        result=parsed(not errors,work,[".".join(map(str,e.absolute_path)) for e in errors],event["data"],work)
        result["validators"]=sorted(e.validator for e in errors)
        return result
