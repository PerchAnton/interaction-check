"""A deliberately narrow JSONL adapter for python-dispatch's real Property API."""
from contextlib import nullcontext
import json
import sys

from pydispatch import Dispatcher, Property


class Counter(Dispatcher):
    count = Property(0)


class Probe:
    def __init__(self):
        self.model = Counter()
        self.log = []
        self.model.bind(count=self.receive)

    def receive(self, instance, value, **kwargs):
        self.log.append(value)

    def step(self, event):
        if event.get("op") == "write" and set(event) == {"op", "values", "locked"}:
            if (type(event["locked"]) is not bool or not isinstance(event["values"], list)
                    or not 1 <= len(event["values"]) <= 100
                    or any(type(v) is not int or abs(v) > 1_000_000 for v in event["values"])):
                raise ValueError("expected 1..100 bounded integers and a boolean lock")
            with self.model.emission_lock("count") if event["locked"] else nullcontext():
                for value in event["values"]:
                    self.model.count = value
        elif event == {"op": "unbind"}:
            self.model.unbind(self.receive)
        else:
            raise ValueError("unsupported event")
        return {"count": self.model.count, "log": list(self.log)}


def main():
    probe = Probe()
    for index, line in enumerate(sys.stdin, 1):
        request = json.loads(line)
        if (set(request) != {"protocol", "id", "event"}
                or type(request["protocol"]) is not int or request["protocol"] != 1
                or type(request["id"]) is not int or request["id"] != index):
            raise ValueError("invalid protocol envelope")
        state = probe.step(request["event"])
        print(json.dumps({"protocol": 1, "id": index, "state": state}), flush=True)


if __name__ == "__main__":
    main()
