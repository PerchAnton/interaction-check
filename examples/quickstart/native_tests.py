"""The same three behaviors checked directly, without a replay runner."""
import unittest

from editor import Editor


class EditorTests(unittest.TestCase):
    def setUp(self):
        self.editor = Editor()
        self.editor.open()

    def test_cancel_keeps_saved(self):
        self.editor.type("Preview")
        self.editor.cancel()
        self.assertEqual(self.editor.saved, "Original")
        self.assertIsNone(self.editor.draft)
        self.editor.open()
        self.assertEqual(self.editor.draft, "Original")

    def test_save_replaces_saved(self):
        self.editor.type("Edited")
        self.editor.save()
        self.assertEqual(self.editor.saved, "Edited")
        self.assertIsNone(self.editor.draft)

    def test_invalid_input_can_be_corrected(self):
        self.editor.type(" ")
        self.editor.save()
        self.assertEqual(self.editor.saved, "Original")
        self.assertEqual(self.editor.draft, " ")
        self.assertEqual(self.editor.error, "Enter a title")
        self.editor.type("Corrected")
        self.editor.save()
        self.assertEqual(self.editor.saved, "Corrected")
        self.assertIsNone(self.editor.draft)
        self.assertIsNone(self.editor.error)


if __name__ == "__main__":
    unittest.main()
