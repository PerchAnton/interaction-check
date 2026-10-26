"""Resolve registered JSON resources without network retrieval."""

from python_protocol import fields, text
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012

from .helpers import mapping


class Consumer:
    """Retain the preceding immutable Registry to observe replacement."""

    def __init__(self):
        self.registry = Registry()
        self.previous = self.registry

    def step(self, event):
        op = event.get("op")
        value = None
        error = None
        if op == "register":
            fields(event, ("op", "uri", "data"))
            uri = text(event["uri"])
            data = mapping(event["data"])
            resource = Resource.from_contents(data, default_specification=DRAFT202012)
            self.previous = self.registry
            self.registry = self.registry.with_resource(uri, resource)
        elif op == "lookup":
            fields(event, ("op", "ref", "previous"))
            if type(event["previous"]) is not bool:
                raise ValueError("previous must be boolean")
            ref = text(event["ref"])
            registry = self.previous if event["previous"] else self.registry
            try:
                value = registry.resolver().lookup(ref).contents
            except Unresolvable as exc:
                error = type(exc).__name__
        else:
            raise ValueError("unsupported event")
        return {
            "value": value,
            "error": error,
            "resources": len(self.registry),
            "previous_resources": len(self.previous),
        }
