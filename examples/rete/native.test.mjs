import test from "node:test";
import assert from "node:assert/strict";
import { NodeEditor } from "rete";
import { create } from "./adapter.mjs";

test("native denied removal leaves the node available for retry", async () => {
  const editor = new NodeEditor();
  let deny = true;
  editor.addPipe(event => event.type === "noderemove" && deny ? undefined : event);
  await editor.addNode({ id: "a" });
  assert.equal(await editor.removeNode("a"), false);
  assert.equal(editor.getNodes().length, 1);
  deny = false;
  assert.equal(await editor.removeNode("a"), true);
  assert.equal(editor.getNodes().length, 0);
});

test("adapter rejects unknown operations and resets the real editor", async () => {
  const adapter = create();
  await assert.rejects(adapter.step({ op: "clear" }), /new must/);
  await adapter.step({ op: "new" });
  await adapter.step({ op: "add_node", id: "a" });
  assert.deepEqual((await adapter.step({ op: "new" })).nodes, []);
  await assert.rejects(adapter.step({ op: "invented" }), /unsupported/);
  await assert.rejects(adapter.step({ op: "clear", expect: {} }), /fields/);
});
