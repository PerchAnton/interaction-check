"""Build a trace from real Python jsonpatch output and an independent desired document."""
from jsonpatch import JsonPatch


def scenario():
    original = {"items": ["a", "b", "c"], "title": "before"}
    desired = {"items": ["b", "c", "a"], "title": "after", "a/b": {"~": 1}}
    patch = JsonPatch.from_diff(original, desired).patch
    return {"schema": 1, "name": "Python-generated patch / Mutative consumer", "steps": [
        {"event": {"op": "new", "data": original}, "expect": {"document": original, "error": None}},
        {"event": {"op": "apply", "patch": patch}, "expect": {"document": desired, "error": None}},
    ]}


if __name__ == "__main__":
    import json
    print(json.dumps(scenario(), indent=2))
