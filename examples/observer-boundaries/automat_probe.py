"""Observe factory failures through public input methods, not private state names."""
from typing import Protocol
from automat import TypeMachineBuilder


class Inputs(Protocol):
    def start(self) -> None: ...
    def read(self) -> str: ...
    def recover(self) -> str: ...


class FactoryAbort(BaseException):
    pass


def probe(explicit_error=False, exception=ValueError, fail=True):
    builder = TypeMachineBuilder(Inputs, list)
    idle = builder.state('idle')

    def make_data(inputs: Inputs, log: list) -> str:
        log.append('factory')
        if fail:
            raise exception('factory failed')
        return 'loaded'

    ready = builder.state('ready', make_data)
    idle.upon(Inputs.start).to(ready).returns(None)
    idle.upon(Inputs.read).loop().returns('idle')

    @ready.upon(Inputs.read).loop()
    def read_ready(inputs: Inputs, log: list, data: str) -> str:
        log.append('read:' + type(data).__name__)
        return data.upper()

    if explicit_error:
        error = builder.error_state('error')
        error.upon(Inputs.read).loop().returns('error')
        error.upon(Inputs.recover).to(idle).returns('recovered')
    log = []
    machine = builder.build()(log)
    observed = {'explicit_error': explicit_error, 'factory_error': None, 'read': None,
                'read_error': None, 'recovery': None, 'log': log}
    try:
        machine.start()
    except (ValueError, FactoryAbort) as exc:
        observed['factory_error'] = type(exc).__name__
    try:
        observed['read'] = machine.read()
    except (AssertionError, AttributeError, TypeError) as exc:
        observed['read_error'] = type(exc).__name__
    if explicit_error and fail:
        observed['recovery'] = machine.recover()
        observed['after_recovery'] = machine.read()
    return observed


if __name__ == '__main__':
    import json
    import sys
    fixed = '--fixed' in sys.argv
    rows = [probe(False, fail=False), probe(False), probe(False, FactoryAbort)]
    if fixed:
        rows += [probe(True), probe(True, FactoryAbort)]
    print(json.dumps(rows, indent=2))
