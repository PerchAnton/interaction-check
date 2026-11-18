"""Native baselines: pinned discrepancies remain explicit observations."""
import unittest
from controllers import atom_controller, traits_controller
from automat_probe import probe, FactoryAbort


class Boundaries(unittest.TestCase):
    def test_atom_replacement_rebinds_and_detaches_old_point(self):
        step = atom_controller()
        first = step({'op': 'write', 'value': 1})
        self.assertEqual(first['callbacks'], [{'name': 'x', 'old': 0, 'new': 1, 'type': 'update'}])
        replaced = step({'op': 'replace', 'value': 2})
        self.assertEqual((replaced['value'], replaced['callbacks']), (2, []))
        old = step({'op': 'write-old', 'value': 99})
        self.assertEqual((old['value'], old['callbacks']), (2, []))
        current = step({'op': 'write', 'value': 3})
        self.assertEqual(current['callbacks'], [{'name': 'x', 'old': 2, 'new': 3, 'type': 'update'}])
        self.assertEqual(len(current['log']), 2)

    def test_atom_observing_parent_and_child_reports_each_change_once(self):
        from atom.api import Atom, Int, List, Typed, observe

        class Point(Atom):
            x = Int()

        class Item(Atom):
            pos = Typed(Point, ())
            seen = List()

            @observe('pos', 'pos.x')
            def record(self, change):
                self.seen.append((change['name'], change.get('oldvalue'), change['value']))

        first, second = Point(x=0), Point(x=2)
        item = Item(pos=first)
        item.seen.clear()
        first.x = 1
        item.pos = second
        first.x = 99
        second.x = 3
        self.assertEqual(item.seen, [('x', 0, 1), ('pos', first, second), ('x', 2, 3)])

    def test_traits_value_updates_but_readonly_property_notification_is_missing(self):
        step = traits_controller()
        for value in [2, 3]:
            observed = step({'op': 'write', 'value': value})
            self.assertEqual(observed['readonly_square'], value * value)
            self.assertEqual(observed['mutable_square'], value * value)
            self.assertEqual(observed['callbacks'], ['mutable.x', 'mutable_square', 'readonly.x'])

    def test_traits_equal_assignment_is_not_a_second_change(self):
        step = traits_controller()
        step({'op': 'write', 'value': 2})
        self.assertEqual(step({'op': 'write', 'value': 2})['callbacks'], [])

    def test_automat_successful_factory_is_a_control(self):
        result = probe(fail=False)
        self.assertEqual(result['read'], 'LOADED')
        self.assertIsNone(result['factory_error'])
        self.assertIsNone(result['read_error'])

    def test_automat_published_factory_failures_leave_inconsistent_data(self):
        for exception in [ValueError, FactoryAbort]:
            with self.subTest(exception=exception):
                result = probe(exception=exception)
                self.assertEqual(result['factory_error'], exception.__name__)
                self.assertEqual(result['read_error'], 'AssertionError')
                self.assertEqual(result['log'], ['factory'])


if __name__ == '__main__':
    unittest.main()
