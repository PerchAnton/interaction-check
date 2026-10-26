from pyee import EventEmitter


def test_once_is_removed_before_reentrant_emit():
    """A once handler must not run again during its own nested emission."""
    ee = EventEmitter()
    calls = []

    @ee.once("event")
    def once_handler(value):
        calls.append(("once", value))
        if value == 1:
            assert ee.emit("event", 2) is True

    @ee.on("event")
    def persistent_handler(value):
        calls.append(("persistent", value))

    assert ee.emit("event", 1) is True
    assert calls == [("once", 1), ("persistent", 2), ("persistent", 1)]
    assert ee.listeners("event") == [persistent_handler]

    assert ee.emit("event", 3) is True
    assert calls[-1] == ("persistent", 3)
    assert len(calls) == 4
