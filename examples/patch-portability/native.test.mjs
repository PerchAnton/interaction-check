import test from 'node:test';
import assert from 'node:assert/strict';
import { immutableJSONPatch, revertJSONPatch } from 'immutable-json-patch';
import { JSONPatcherProxy } from 'jsonpatcherproxy';
test('move then inverse restores the original array without changing the input', () => {
  const original = { list: ['a', 'b', 'c'] };
  const copy = structuredClone(original);
  const patch = [{ op: 'move', from: '/list/0', path: '/list/2' }];
  const inverse = revertJSONPatch(original, patch);
  const changed = immutableJSONPatch(original, patch);
  assert.deepEqual(changed, { list: ['b', 'c', 'a'] });
  assert.deepEqual(immutableJSONPatch(changed, inverse), copy);
  assert.deepEqual(original, copy);
});
test('producer callbacks, cumulative log, and consumer state are separate', () => {
  const original = { 'a/b': 1, list: ['a', 'b', 'c'] };
  let consumer = structuredClone(original);
  const log = [];
  const observer = new JSONPatcherProxy(structuredClone(original));
  const proxy = observer.observe(false, patch => {
    log.push(structuredClone(patch));
    consumer = immutableJSONPatch(consumer, [patch]);
  });
  proxy['a/b'] = 2;
  assert.deepEqual(log, [{ op: 'replace', path: '/a~1b', value: 2 }]);
  const previous = log.length;
  proxy.list.splice(1, 1);
  assert.ok(log.length > previous);
  assert.deepEqual(consumer, JSON.parse(JSON.stringify(proxy)));
  observer.pause();
  proxy['a/b'] = 3;
  assert.equal(consumer['a/b'], 2);
  observer.resume();
  proxy['a/b'] = 4;
  assert.equal(consumer['a/b'], 4);
  observer.disableTraps();
});
