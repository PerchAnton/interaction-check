"""Invalid trace arguments must not partially mutate native fixtures."""

import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE.parent))
sys.path.insert(0, str(BASE))
import replay
from factory import create


class InputBoundaryTests(unittest.TestCase):
    """Assert native values and delivered notifications after rejected batches."""

    def test_invalid_write_batch_does_not_apply_earlier_members(self):
        for name, options in (
            ("param", {"mode": "batch"}),
            ("traitlets", {"hold": True}),
        ):
            with self.subTest(name=name):
                consumer = create(name)
                with self.assertRaises(ValueError):
                    consumer.step(
                        {
                            "op": "write",
                            **options,
                            "updates": [
                                {"field": "count", "value": 1},
                                {"field": "count", "value": "bad"},
                            ],
                        }
                    )
                self.assertEqual(consumer.model.count, 0)
                self.assertEqual(consumer.model.label, "A")
                self.assertEqual(consumer.log, [])

    def test_invalid_emission_batch_does_not_emit_earlier_members(self):
        for name, event in (
            ("psygnal", {"op": "emit", "mode": "plain"}),
            ("python-dispatch", {"op": "write", "locked": False}),
        ):
            with self.subTest(name=name):
                consumer = create(name)
                with self.assertRaises(ValueError):
                    consumer.step({**event, "values": [1, "bad"]})
                self.assertEqual(consumer.log, [])
                if name == "python-dispatch":
                    self.assertEqual(consumer.model.count, 0)

    def test_string_options_cannot_enable_mutation_modes(self):
        consumer = create("jsonpatch")
        consumer.step({"op": "new", "data": {"count": 1}})
        with self.assertRaises(ValueError):
            consumer.step(
                {
                    "op": "apply",
                    "patch": [{"op": "replace", "path": "/count", "value": 2}],
                    "in_place": "false",
                }
            )
        self.assertEqual(consumer.document, {"count": 1})
        consumer = create("python-dispatch")
        with self.assertRaises(ValueError):
            consumer.step({"op": "write", "values": [1], "locked": "false"})
        self.assertEqual(consumer.model.count, 0)
        self.assertEqual(consumer.log, [])

    def test_invalid_glom_path_cannot_create_intermediate_objects(self):
        consumer = create("glom")
        with self.assertRaises(ValueError):
            consumer.step({"op": "assign", "path": ["settings", 123], "value": 1})
        self.assertEqual(consumer.document, {})

    def test_observing_cache_does_not_add_hits(self):
        consumer = create("boltons")
        first = consumer.step({"op": "put", "key": "a", "value": 1})
        second = consumer.step({"op": "put", "key": "b", "value": 2})
        self.assertEqual(first["hits"], 0)
        self.assertEqual(second["hits"], 0)
        self.assertEqual(second["entries"], {"a": 1, "b": 2})

    def test_publishers_do_not_share_listeners_or_topic_state(self):
        first = create("pypubsub")
        second = create("pypubsub")
        first.step({"op": "subscribe", "topic": "document"})
        second.step({"op": "send", "topic": "document", "data": {"value": 1}})
        self.assertEqual(first.log, [])
        first.step({"op": "send", "topic": "document", "data": {"value": 2}})
        self.assertEqual(first.log, [2])
        self.assertEqual(second.log, [])

    def test_factory_does_not_import_unlisted_modules(self):
        for name in ("os", "../jsonpatch", "consumers.helpers"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                create(name)

    def test_interrupted_runner_is_not_reported_as_success(self):
        with (
            patch.object(sys, "argv", ["replay.py"]),
            patch.object(replay, "MODULES", {"pydantic": "pydantic_model"}),
            patch.object(
                replay.subprocess,
                "run",
                return_value=types.SimpleNamespace(returncode=-9),
            ),
        ):
            self.assertEqual(replay.main(), 1)

    def test_relative_reports_stay_in_callers_directory(self):
        previous = Path.cwd()
        with tempfile.TemporaryDirectory() as directory:
            try:
                os.chdir(directory)
                expected = Path(directory).resolve() / "reports" / "pydantic.json"
                with (
                    patch.object(sys, "argv", ["replay.py", "--reports", "reports"]),
                    patch.object(replay, "MODULES", {"pydantic": "pydantic_model"}),
                    patch.object(
                        replay.subprocess,
                        "run",
                        return_value=types.SimpleNamespace(returncode=0),
                    ) as run,
                ):
                    self.assertEqual(replay.main(), 0)
                    command = run.call_args.args[0]
                    self.assertEqual(
                        command[command.index("--report") + 1], str(expected)
                    )
                    self.assertTrue(expected.parent.is_dir())
            finally:
                os.chdir(previous)


if __name__ == "__main__":
    unittest.main()
