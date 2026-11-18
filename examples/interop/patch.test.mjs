import { test } from 'node:test';
import assert from 'node:assert/strict';
import { apply } from 'mutative';
import { applyBridge } from './patch-bridge.mjs';
import { createPatchAdapter } from './patch-adapter.mjs';

test('native Mutative does not accept a move operation', () => {
  assert.throws(() => apply({ a: 1 }, [{ op: 'move', from: ['a'], path: ['b'] }]));
});
test('moving within one array resolves the destination after removal', () => {
  const before = { items: ['a', 'b', 'c'] };
  assert.deepEqual(applyBridge(before, [{ op: 'move', from: '/items/0', path: '/items/2' }]), { items: ['b', 'c', 'a'] });
  assert.deepEqual(before, { items: ['a', 'b', 'c'] });
});
test('escaped paths and copy produce independent JSON values', () => {
  const result = applyBridge({ 'a/b': { '~': { n: 1 } } }, [
    { op: 'copy', from: '/a~1b/~0', path: '/copy' }, { op: 'replace', path: '/copy/n', value: 2 }]);
  assert.deepEqual(result, { 'a/b': { '~': { n: 1 } }, copy: { n: 2 } });
});
test('failed patches preserve the published document, including failed move targets', () => {
  const step = createPatchAdapter(); step({ op: 'new', data: { n: 1, list: ['a'] } });
  assert.deepEqual(step({ op: 'apply', patch: [{ op: 'replace', path: '/n', value: 2 },
    { op: 'remove', path: '/missing' }] }), { document: { n: 1, list: ['a'] }, error: 'rejected' });
  assert.deepEqual(step({ op: 'apply', patch: [{ op: 'move', from: '/list/0', path: '/missing/0' }] }),
    { document: { n: 1, list: ['a'] }, error: 'rejected' });
});
test('bounds, malformed pointers and unsupported operations reject', () => {
  for (const patch of [[{ op: 'add', path: '/x/3', value: 1 }], [{ op: 'replace', path: '/x/00', value: 1 }],
    [{ op: 'remove', path: '/x/-' }], [{ op: 'copy', from: '/x', path: '/bad~2' }],
    [{ op: 'move', from: '/x', path: '/x/0' }], [{ op: 'add', path: '/__proto__/polluted', value: true }],
    [{ op: 'test', path: '/x', value: [] }], [{ op: 'replace', path: '', value: {} }]]) {
    assert.throws(() => applyBridge({ x: [] }, patch));
  }
  assert.equal({}.polluted, undefined);
});
test('append, object replacement, empty tokens and a no-op move', () => {
  assert.deepEqual(applyBridge({ '': 1, x: ['a'], a: 2 }, [{ op: 'move', from: '/a', path: '/a' },
    { op: 'add', path: '/x/-', value: 'b' }, { op: 'copy', from: '/', path: '/a' }]),
    { '': 1, x: ['a', 'b'], a: 1 });
});
