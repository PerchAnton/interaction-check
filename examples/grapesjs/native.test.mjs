import test from "node:test";
import assert from "node:assert/strict";
import {create} from "./adapter.mjs";
import {fixture} from './adapter.mjs';
test('real UndoManager ignores an unchanged model property and preserves redo', () => {
  const {editor,component}=fixture();
  try {
    component.set('name','one'); component.set('name','two'); editor.UndoManager.undo(false);
    assert.equal(component.get('name'),'one'); assert.equal(editor.UndoManager.hasRedo(),true);
    component.set('name','one'); assert.equal(editor.UndoManager.hasRedo(),true);
    editor.UndoManager.redo(false); assert.equal(component.get('name'),'two');
  } finally { editor.destroy(); }
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
