"""Small installed-library observations; callbacks and values remain distinct."""
import json
import sys


def atom_controller():
    from atom.api import Atom, Int, List, Typed, observe

    class Point(Atom):
        x = Int()

    class Item(Atom):
        pos = Typed(Point, ())
        calls = List()

        @observe('pos.x')
        def changed(self, event):
            self.calls.append({'name': event['name'], 'old': event.get('oldvalue'),
                               'new': event.get('value'), 'type': event['type']})

    first = Point(x=0)
    item = Item(pos=first)
    log = []

    def step(event):
        item.calls.clear()
        op = event['op']
        if op == 'write':
            item.pos.x = event['value']
        elif op == 'replace':
            item.pos = Point(x=event['value'])
        elif op == 'write-old':
            first.x = event['value']
        elif op != 'snapshot':
            raise ValueError(op)
        calls = list(item.calls)
        log.extend(calls)
        return {'value': item.pos.x, 'callbacks': calls, 'log': list(log)}
    return step


def traits_controller():
    from traits.api import Float, HasTraits, Instance, Property, ReadOnly

    class Point(HasTraits):
        x = Float(0.0)

    class Pair(HasTraits):
        mutable = Instance(Point)
        readonly = ReadOnly()
        mutable_square = Property(observe='mutable.x')
        readonly_square = Property(observe='readonly.x')

        def _get_mutable_square(self):
            return self.mutable.x ** 2

        def _get_readonly_square(self):
            return self.readonly.x ** 2

    point = Point()
    pair = Pair(mutable=point, readonly=point)
    calls, log = [], []
    for name in ['mutable.x', 'readonly.x', 'mutable_square', 'readonly_square']:
        pair.observe(lambda event, name=name: calls.append(name), name)

    def step(event):
        calls.clear()
        if event['op'] == 'write':
            point.x = event['value']
        elif event['op'] != 'snapshot':
            raise ValueError(event['op'])
        # This example checks presence, not relative dispatch order.
        current = sorted(calls)
        log.extend(current)
        return {'value': point.x, 'mutable_square': pair.mutable_square,
                'readonly_square': pair.readonly_square,
                'callbacks': current, 'log': list(log)}
    return step


if __name__ == '__main__':
    step = {'atom': atom_controller, 'traits': traits_controller}[sys.argv[1]]()
    for line in sys.stdin:
        request = json.loads(line)
        if set(request) != {'id', 'event', 'protocol'} or request['protocol'] != 1:
            raise ValueError('Invalid protocol')
        print(json.dumps({'protocol': 1, 'id': request['id'], 'state': step(request['event'])}), flush=True)
