"""Application-owned copy/publish boundary; native behavior is tested separately."""
from copy import deepcopy
import json
import sys
from jsonpath.exceptions import JSONPatchError, JSONPointerError
from jsonpatch import JsonPatchException
from jsonpointer import JsonPointerException

PATCH_ERRORS = (JSONPatchError, JSONPointerError, JsonPatchException, JsonPointerException)


def apply(library, document, patch):
    if library == "jsonpath":
        from jsonpath.patch import JSONPatch
        return JSONPatch(patch, unicode_escape=False).apply(document)
    if library == "jsonpatch":
        import jsonpatch
        return jsonpatch.apply_patch(document, patch, in_place=True)
    if library == "merge":
        import json_merge_patch
        return json_merge_patch.merge(document, patch)
    raise ValueError("unknown library")


class Adapter:
    def __init__(self, library):
        self.library = library
        self.document = None

    def step(self, event):
        error = None
        if event["op"] == "new":
            self.document = deepcopy(event["data"])
        elif event["op"] in ("apply", "merge"):
            candidate = deepcopy(self.document)
            try:
                candidate = apply(self.library, candidate, event["patch"])
            except PATCH_ERRORS:
                # Import/process failures remain fatal; patch rejection is an observation.
                error = "rejected"
            else:
                self.document = candidate
        else:
            raise ValueError("unknown event")
        return {"document": deepcopy(self.document), "error": error}


if __name__ == "__main__":
    adapter = Adapter(sys.argv[1])
    for line in sys.stdin:
        request = json.loads(line)
        if set(request) != {"protocol", "id", "event"} or request["protocol"] != 1:
            raise ValueError("invalid protocol")
        result = adapter.step(request["event"])
        print(json.dumps({"protocol": 1, "id": request["id"], "state": result}, ensure_ascii=False), flush=True)
