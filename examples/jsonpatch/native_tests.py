"""A rejected in-place option must leave the adapter's document intact."""
import unittest

from adapter import Consumer


class JsonPatchInputTests(unittest.TestCase):
    def test_string_flag_cannot_request_an_in_place_write(self):
        consumer = Consumer()
        consumer.step({"op": "new", "data": {"count": 1}})
        with self.assertRaises(ValueError):
            consumer.step({
                "op": "apply",
                "patch": [{"op": "replace", "path": "/count", "value": 2}],
                "in_place": "false",
            })
        self.assertEqual(consumer.document, {"count": 1})
