"""Explicit consumer allowlist: traces cannot select arbitrary import targets."""

import importlib

MODULES = {
    "pydantic": "pydantic_model",
    "cerberus": "cerberus_validation",
    "msgspec": "msgspec_validation",
    "jsonschema": "jsonschema_validation",
    "schema": "schema_validation",
    "referencing": "references",
    "param": "parameters",
    "traitlets": "traits",
    "pypubsub": "pubsub_topics",
    "pyee": "pyee_events",
    "psygnal": "psygnal_signals",
    "python-dispatch": "dispatch_properties",
    "rxpy": "rx_streams",
    "transitions": "transitions_machine",
    "python-statemachine": "state_machine",
    "jsonpatch": "json_patches",
    "dictdiffer": "dictionary_diffs",
    "deepdiff": "deep_diffs",
    "glom": "glom_paths",
    "boltons": "boltons_cache",
}


def create(name):
    """Create one independent native fixture for this adapter process."""
    if name not in MODULES:
        raise ValueError("unknown consumer")
    return importlib.import_module("consumers." + MODULES[name]).Consumer()
