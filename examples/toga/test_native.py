import unittest
from adapter import Adapter

class NativeTests(unittest.TestCase):
    def test_native_selection_tracks_removal_and_repopulation(self):
        import toga
        changes = []
        widget = toga.Selection(items=['a', 'b'])
        widget.on_change = lambda *_args, **_kwargs: changes.append(widget.value)
        widget.value = 'b'
        widget.items.remove(widget.items[0])
        self.assertEqual(widget.value, 'b')
        self.assertEqual(changes, ['b'])
        widget.items.clear()
        self.assertIsNone(widget.value)
        widget.items.append('c')
        self.assertEqual(widget.value, 'c')
        self.assertEqual(changes, ['b', None, 'c'])

    def test_adapter_boundary(self):
        adapter = Adapter()
        with self.assertRaises(ValueError): adapter.step({'op':'unknown'})
        with self.assertRaises(ValueError): adapter.step({'op':'new','expect':{}})
        adapter.step({'op':'new'})
        with self.assertRaises(ValueError): adapter.step({'op':'unknown'})

if __name__ == '__main__': unittest.main()
