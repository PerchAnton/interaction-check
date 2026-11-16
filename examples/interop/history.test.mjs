import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHistoryAdapter } from './history-adapter.mjs';

test('native zundo 2.3.0 undo(0) loses the store value', () => {
  const step = createHistoryAdapter({ guarded: false }); step({ op: 'new' }); step({ op: 'set', value: 1 });
  assert.equal(step({ op: 'undo', steps: 0 }).missing, true);
});
test('guarded invalid counts preserve state, both histories and subscriptions', () => {
  const step = createHistoryAdapter(); step({ op: 'new' }); step({ op: 'set', value: 1 });
  step({ op: 'set', value: 2 }); const before = step({ op: 'undo' });
  for (const op of ['undo', 'redo']) for (const steps of [0, -1, 1.5, '1', null, true, {}, 2 ** 53]) {
    const after = step({ op, steps }); assert.deepEqual(after, { ...before, callbacks: [] });
  }
});
test('large positive counts reach the boundary; redo restores the sequence', () => {
  const step = createHistoryAdapter(); step({ op: 'new' }); step({ op: 'set', value: 1 }); step({ op: 'set', value: 2 });
  const undo = step({ op: 'undo', steps: 99 }); assert.equal(undo.value, 0); assert.deepEqual(undo.past, []);
  const redo = step({ op: 'redo', steps: 99 }); assert.equal(redo.value, 2); assert.deepEqual(redo.future, []);
  assert.equal(redo.callbacks.length, 1);
});
