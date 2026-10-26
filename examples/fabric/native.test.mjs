import test from "node:test";
import assert from "node:assert/strict";
import {create} from "./adapter.mjs";
import {fixture} from './adapter.mjs';
test('real group removal and re-add retain scene centers after translation', () => {
  const {a,b,group}=fixture();
  try {
    group.set({left:group.left+5,top:group.top+2}); group.setCoords();
    const before=a.getCenterPoint(); const other=b.getCenterPoint();
    group.remove(a); assert.ok(a.getCenterPoint().eq(before)); assert.ok(b.getCenterPoint().eq(other));
    group.add(a); assert.ok(a.getCenterPoint().eq(before)); assert.ok(b.getCenterPoint().eq(other));
  } finally { group.dispose(); }
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
