import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createEventsAdapter } from './events-adapter.mjs';

test('native EventEmitter2 distinguishes the two newListener names', () => {
  const step = createEventsAdapter({ normalized: false }); step({ op: 'new' });
  step({ op: 'on', name: 'newListener', listener: 'watch' }); step({ op: 'write', value: 7 });
  assert.deepEqual(step({ op: 'emit', name: 'newListener' }).callbacks, []);
  assert.deepEqual(step({ op: 'emit', name: ['newListener'] }).callbacks, [{ listener: 'watch', value: 7 }]);
});
test('narrow normalization makes both forms consistent with the native string route', () => {
  const step = createEventsAdapter(); step({ op: 'new' }); step({ op: 'on', name: 'newListener', listener: 'watch' });
  assert.deepEqual(step({ op: 'emit', name: 'newListener' }).log, []);
  assert.deepEqual(step({ op: 'emit', name: ['newListener'] }).log, []);
});
test('writes, callbacks and accumulated log are different observations', () => {
  const step = createEventsAdapter(); step({ op: 'new' });
  step({ op: 'on', name: 'data.*', listener: 'first' }); step({ op: 'on', name: 'data.*', listener: 'second' });
  const written = step({ op: 'write', value: 7 }); assert.equal(written.writes, 1); assert.deepEqual(written.log, []);
  const emitted = step({ op: 'emit', name: ['data', 'ready'] });
  assert.deepEqual(emitted.callbacks.map(item => item.listener), ['first', 'second']);
  const again = step({ op: 'emit', name: 'data.ready' });
  assert.equal(again.callbacks.length, 2); assert.equal(again.log.length, 4); assert.equal(again.writes, 1);
});
