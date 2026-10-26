import test from "node:test";
import assert from "node:assert/strict";
import {create} from "./adapter.mjs";
import {applyNodeChanges} from '@xyflow/react';
test('unknown changes preserve unrelated nodes and removed nodes stay removed', () => {
  const nodes=[{id:'a',position:{x:0,y:0},data:{}}];
  assert.strictEqual(applyNodeChanges([{type:'select',id:'missing',selected:true}],nodes)[0],nodes[0]);
  const removed=applyNodeChanges([{type:'remove',id:'a'}],nodes);
  assert.deepEqual(applyNodeChanges([{type:'position',id:'a',position:{x:9,y:9}}],removed),[]);
  assert.deepEqual(nodes[0].position,{x:0,y:0});
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
