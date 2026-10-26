"""Check trace arguments without predicting native library results."""

from copy import deepcopy

from python_protocol import fields, text


def integer(value):
    """Bound counters while preserving invalid domain values for validation."""
    if type(value) is not int or not -10000 <= value <= 10000:
        raise ValueError("expected integer in [-10000, 10000]")
    return value


def mapping(value):
    """Isolate a bounded request object before passing it to native code."""
    if not isinstance(value, dict) or len(value) > 100:
        raise ValueError("expected object with at most 100 fields")
    return deepcopy(value)


def values(value):
    """Validate a whole emission batch before emitting its first member."""
    if not isinstance(value, list) or len(value) > 64:
        raise ValueError("expected at most 64 values")
    return [integer(x) for x in value]


def updates(value):
    """Check every field in a write batch before changing native state."""
    if not isinstance(value, list) or len(value) > 64:
        raise ValueError("expected at most 64 updates")
    result = []
    for item in value:
        fields(item, ("field", "value"))
        if item["field"] not in ("count", "label"):
            raise ValueError("unsupported field")
        result.append(
            (
                item["field"],
                integer(item["value"])
                if item["field"] == "count"
                else text(item["value"]),
            )
        )
    return result


def parsed(valid, output, paths, original, working):
    """Report native output and actual input mutation, not expected values."""
    return {
        "valid": valid,
        "output": output,
        "paths": sorted(paths),
        "keys": sorted(output) if isinstance(output, dict) else [],
        "input_unchanged": original == working,
    }
