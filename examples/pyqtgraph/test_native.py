import unittest
from adapter import Adapter, fixture

class NativeTests(unittest.TestCase):
    def test_native_batch_and_restore(self):
        host = Adapter()
        root = fixture()
        changes = []
        root.sigTreeStateChanged.connect(lambda *_: changes.append(True))
        saved = root.saveState()
        with root.treeChangeBlocker():
            root.child('left').setValue(7)
            root.child('right').setValue(9)
        self.assertEqual(len(changes), 1)
        root.child('left').setValue(7)
        self.assertEqual(len(changes), 1)
        root.restoreState(saved)
        self.assertEqual(root.child('left').value(), 1)
        self.assertEqual(root.child('right').value(), 2)

    def test_adapter_boundary(self):
        adapter = Adapter()
        with self.assertRaises(ValueError): adapter.step({'op':'unknown'})
        with self.assertRaises(ValueError): adapter.step({'op':'new','expect':{}})
        adapter.step({'op':'new'})
        with self.assertRaises(ValueError): adapter.step({'op':'unknown'})

if __name__ == '__main__': unittest.main()
