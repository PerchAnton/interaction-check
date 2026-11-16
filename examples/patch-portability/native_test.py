"""Native tests are enough when no cross-runtime trace needs to be shared."""
from copy import deepcopy
import unittest
from python_adapter import apply, Adapter, PATCH_ERRORS


class NativeTests(unittest.TestCase):
    def test_in_place_failure_is_not_atomic(self):
        for library in ("jsonpath", "jsonpatch"):
            with self.subTest(library=library):
                document = {"n": 1}
                with self.assertRaises(PATCH_ERRORS):
                    apply(library, document, [{"op": "replace", "path": "/n", "value": 2},
                                              {"op": "test", "path": "/n", "value": 9}])
                self.assertEqual(document, {"n": 2})

    def test_copy_publish_boundary_keeps_failed_batch_private(self):
        for library in ("jsonpath", "jsonpatch"):
            with self.subTest(library=library):
                a = Adapter(library)
                a.step({"op": "new", "data": {"n": 1}})
                self.assertEqual(a.step({"op": "apply", "patch": [
                    {"op": "replace", "path": "/n", "value": 2},
                    {"op": "test", "path": "/n", "value": 9}]}),
                    {"document": {"n": 1}, "error": "rejected"})

    def test_merge_patch_is_separate_and_idempotent(self):
        before = {"delete": 1, "items": [1, 2], "keep": True}
        patch = {"delete": None, "items": [3]}
        expected = {"items": [3], "keep": True}
        self.assertEqual(apply("merge", deepcopy(before), patch), expected)
        self.assertEqual(apply("merge", deepcopy(expected), patch), expected)


if __name__ == "__main__":
    unittest.main()
