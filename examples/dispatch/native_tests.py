"""Equivalent behavior checks without interaction-check or an adapter."""
import unittest
from pydispatch import Dispatcher, Property


class Model(Dispatcher):
    count = Property(0)


class NativeTests(unittest.TestCase):
    def setUp(self):
        self.model = Model()
        self.log = []
        self.model.bind(count=self.receive)

    def receive(self, instance, value, **kwargs):
        self.log.append(value)

    def test_equal_write(self):
        self.model.count = 1
        self.model.count = 1
        self.assertEqual(self.log, [1])

    def test_lock_coalesces(self):
        with self.model.emission_lock("count"):
            for value in [2, 3, 4]:
                self.model.count = value
        self.assertEqual(self.model.count, 4)
        self.assertEqual(self.log, [4])

    def test_unbind_keeps_writes(self):
        self.model.unbind(self.receive)
        self.model.count = 5
        self.assertEqual(self.model.count, 5)
        self.assertEqual(self.log, [])
