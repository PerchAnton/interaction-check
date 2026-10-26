import io
import json
import unittest

from python_protocol import LIMIT, serve
from interaction_check import CheckError


class ProtocolTests(unittest.TestCase):
    def packet(self, **updates):
        packet = {"protocol": 1, "id": 1, "event": {"op": "new"}}
        packet.update(updates)
        return (json.dumps(packet) + "\n").encode()

    def test_event_is_only_input_and_utf8_reply_is_one_line(self):
        seen = []
        output = io.BytesIO()
        serve(lambda event: seen.append(event) or {"text": "Тест"}, io.BytesIO(self.packet()), output)
        self.assertEqual(seen, [{"op": "new"}])
        self.assertEqual(json.loads(output.getvalue()), {"protocol": 1, "id": 1, "state": {"text": "Тест"}})
        self.assertEqual(output.getvalue().count(b"\n"), 1)

    def test_rejects_invalid_ids_and_protocol_before_call(self):
        for updates in ({"id": True}, {"id": -1}, {"id": 2**53}, {"protocol": True}, {"protocol": 2}, {"event": []}, {"expect": {}}):
            with self.subTest(updates=updates), self.assertRaises(ValueError):
                serve(lambda _: self.fail("invalid packet reached adapter"), io.BytesIO(self.packet(**updates)), io.BytesIO())

    def test_rejects_duplicate_keys_and_nonfinite_numbers(self):
        for packet in (b'{"protocol":1,"id":1,"id":2,"event":{}}\n', b'{"protocol":1,"id":1,"event":{"value":NaN}}\n'):
            with self.subTest(packet=packet), self.assertRaises(CheckError):
                serve(lambda _: {}, io.BytesIO(packet), io.BytesIO())

    def test_bounds_both_directions(self):
        with self.assertRaises(ValueError):
            serve(lambda _: {}, io.BytesIO(b" " * (LIMIT + 1)), io.BytesIO())
        with self.assertRaises(ValueError):
            serve(lambda _: {"text": "x" * LIMIT}, io.BytesIO(self.packet()), io.BytesIO())

    def test_requires_object_state(self):
        with self.assertRaises(ValueError):
            serve(lambda _: [], io.BytesIO(self.packet()), io.BytesIO())


if __name__ == "__main__":
    unittest.main()
