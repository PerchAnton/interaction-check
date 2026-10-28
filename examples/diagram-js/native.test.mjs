import test from "node:test";
import assert from "node:assert/strict";
import {create} from "./adapter.mjs";
import {fixture} from './adapter.mjs';
test('real command history branches after undo and a new command', () => {
  const {stack,model}=fixture();
  stack.execute('value.set',{value:2}); stack.execute('value.set',{value:4});
  stack.undo(); assert.equal(model.value,2); assert.equal(stack.canRedo(),true);
  stack.execute('value.set',{value:7}); assert.equal(stack.canRedo(),false);
  stack.undo(); assert.equal(model.value,2); stack.redo(); assert.equal(model.value,7);
  assert.equal(stack.canExecute('value.set',{value:11}),false);
});
test('adapter rejects missing initialization, expectations, and unknown operations', async () => {
  const adapter=create();
  try {
    await assert.rejects(async () => adapter.step({op:'unknown'}));
    await assert.rejects(async () => adapter.step({op:'new',expect:{}}));
    await adapter.step({op:'new'});
    await assert.rejects(async () => adapter.step({op:'unknown'}));
  } finally { await adapter.close(); }
});
