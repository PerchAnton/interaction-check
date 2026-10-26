"""Observe Boltons LRU eviction and real cache hit/miss counters."""

from boltons.cacheutils import LRU
from python_protocol import fields, text

from .helpers import integer


class Consumer:
    """Snapshot using items() so observation itself does not create cache hits."""

    def __init__(self):
        self.cache = LRU(max_size=2)

    def step(self, event):
        op = event.get("op")
        value = None
        if op == "put":
            fields(event, ("op", "key", "value"))
            key = text(event["key"])
            number = integer(event["value"])
            self.cache[key] = number
        elif op == "get":
            fields(event, ("op", "key"))
            value = self.cache.get(text(event["key"]))
        elif op == "clear":
            fields(event, ("op",))
            self.cache.clear()
        else:
            raise ValueError("unsupported event")
        return {
            "entries": dict(sorted(self.cache.items())),
            "value": value,
            "hits": self.cache.hit_count,
            "misses": self.cache.miss_count,
            "soft_misses": self.cache.soft_miss_count,
        }
