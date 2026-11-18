import assert from 'node:assert/strict';
import test from 'node:test';
import { tinyController, topicProbe } from './events.mjs';

test('unknown callback removal preserves two existing listeners', () => {
  const step = tinyController();
  for (const name of ['a', 'b']) step({ op: 'on', name });
  step({ op: 'off', name: 'unknown' });
  assert.deepEqual(step({ op: 'emit', value: 4 }).callbacks, [['a', 4], ['b', 4]]);
});
test('repeated cleanup preserves the other listener', () => {
  const step = tinyController();
  for (const name of ['a', 'b']) step({ op: 'on', name });
  step({ op: 'off', name: 'a' }); step({ op: 'off', name: 'a' });
  assert.deepEqual(step({ op: 'emit', value: 5 }).callbacks, [['b', 5]]);
});
test('once can be removed by its original callback', () => {
  const step = tinyController();
  step({ op: 'once', name: 'a' }); step({ op: 'on', name: 'b' });
  step({ op: 'off', name: 'a' });
  assert.deepEqual(step({ op: 'emit', value: 6 }).callbacks, [['b', 6]]);
});
for (const method of ['clearSubscriptions', 'unsubscribe']) for (const parent of [true, false]) {
  test(`PubSubJS 1.9.5 known prefix discrepancy: ${method}, parent=${parent}`, () => {
    assert.deepEqual(topicProbe(method, parent).callbacks, [],
      'Published version removes entering too; this is a retained discrepancy, not desired semantics.');
  });
}
