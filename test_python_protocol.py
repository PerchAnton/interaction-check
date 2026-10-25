"""Protocol boundary tests that require no third-party widget packages."""

import io
import json
import types
import unittest
from unittest.mock import patch

from adapters import python_protocol as protocol


class PythonProtocolTests(unittest.TestCase):
    """Reject oracle leakage and malformed envelopes before native execution."""

    def read(self, data):
        """Provide a bounded in-memory stdin for one request."""
        with patch.object(
            protocol.sys, "stdin", types.SimpleNamespace(buffer=io.BytesIO(data))
        ):
            return protocol.read_request()

    def test_rejects_expectation_in_envelope(self):
        with self.assertRaises(ValueError):
            self.read(b'{"protocol":1,"id":0,"event":{},"expect":{"value":"fake"}}')

    def test_rejects_wrong_protocol_and_identifier_types(self):
        for version, identifier in [(True, 1), (2, 1), (1, True), (1, -1)]:
            with (
                self.subTest(version=version, identifier=identifier),
                self.assertRaises(ValueError),
            ):
                self.read(
                    json.dumps(
                        {"protocol": version, "id": identifier, "event": {}}
                    ).encode()
                )

    def test_rejects_oversized_or_invalid_utf8(self):
        for data in (b"x" * 65537, b"\xff"):
            with self.assertRaises((ValueError, UnicodeError)):
                self.read(data)

    def test_eof_and_response_identity(self):
        self.assertIsNone(self.read(b""))
        request = self.read(b'{"protocol":1,"id":123,"event":{"op":"new"}}')
        with patch.object(protocol.sys, "stdout", io.StringIO()) as output:
            protocol.emit(request, {"value": "actual"})
        self.assertEqual(
            json.loads(output.getvalue()),
            {"protocol": 1, "id": 123, "state": {"value": "actual"}},
        )

    def test_boolean_options_are_not_truthy_strings(self):
        with self.assertRaises(ValueError):
            protocol.fields({"op": "new", "readonly": "false"}, ("op",), ("readonly",))


if __name__ == "__main__":
    unittest.main()
