"""Translate protocol-1 events into calls on the teaching model."""
import json
import sys

from editor import Editor


def main():
    editor = Editor()
    for line in sys.stdin:
        request = json.loads(line)
        if (type(request.get("protocol")) is not int or request["protocol"] != 1
                or type(request.get("id")) is not int):
            raise ValueError("expected protocol 1 and an integer id")
        event = request["event"]
        operation = event["op"]
        fields = {"op", "text"} if operation == "type" else {"op"}
        if set(event) != fields:
            raise ValueError("unexpected event fields")
        if operation == "type":
            if not isinstance(event["text"], str):
                raise ValueError("text must be a string")
            editor.type(event["text"])
        elif operation == "open":
            editor.open()
        elif operation == "save":
            editor.save()
        elif operation == "cancel":
            editor.cancel()
        else:
            raise ValueError("unknown operation")
        print(json.dumps({"protocol": 1, "id": request["id"], "state": {
            "saved": editor.saved, "draft": editor.draft, "error": editor.error,
        }}, ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
