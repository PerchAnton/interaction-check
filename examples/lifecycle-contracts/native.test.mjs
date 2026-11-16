import test from 'node:test';
import assert from 'node:assert/strict';
import { emitter, controller } from './emitter.mjs';
import { Signal } from 'typed-signals';

for (const library of ['mitt', 'typed-signals', 'emittery', 'contra']) {
  test(`${library}: writes are not emissions, unsubscribe stops later callbacks`, async () => {
    const step = controller(library);
    await step({op:'new'}); await step({op:'on',listener:'a'});
    const write = await step({op:'write',value:7});
    assert.deepEqual(write, {value:7,writes:1,emissions:0,callbacks:[],log:[]});
    const sent = await step({op:'emit'});
    assert.deepEqual(sent.callbacks, [['a',7]]);
    await step({op:'off',listener:'a'});
    const off = await step({op:'emit'});
    assert.deepEqual(off.callbacks, []); assert.deepEqual(off.log, [['a',7]]);
  });
  test(`${library}: unknown-unsubscribe behavior (contra has a known mismatch)`, async () => {
    const bus = emitter(library); const log = [];
    bus.on(value => log.push(value)); bus.off(() => {}); await bus.emit(3);
    // Keep the known published contra discrepancy explicit, not a passing contract.
    assert.deepEqual(log, library === 'contra' ? [] : [3]);
  });
}
test('typed-signals 3: order is an options object, not a positional number', () => {
  const signal = new Signal(); const seen = [];
  signal.connect(() => seen.push('late'), {order:1});
  signal.connect(() => seen.push('early'), {order:0});
  signal.emit(); assert.deepEqual(seen, ['early','late']);
});
