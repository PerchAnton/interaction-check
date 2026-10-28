import unittest
from adapter import Adapter, fixture

class NativeTests(unittest.TestCase):
    def test_native_locked_selection_survives_mixed_delete(self):
        layers = fixture()
        a, b = layers
        a.locked = True
        layers.selection.update([a, b])
        layers.remove_selected()
        self.assertEqual(list(layers), [a])
        self.assertEqual(set(layers.selection), {a})
        a.locked = False
        layers.remove_selected()
        self.assertEqual(list(layers), [])

    def test_adapter_boundary(self):
        adapter = Adapter()
        with self.assertRaises(ValueError): adapter.step({'op':'unknown'})
        with self.assertRaises(ValueError): adapter.step({'op':'new','expect':{}})
        adapter.step({'op':'new'})
        with self.assertRaises(ValueError): adapter.step({'op':'unknown'})

if __name__ == '__main__': unittest.main()
