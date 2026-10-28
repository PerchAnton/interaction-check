import test from "node:test";
import assert from "node:assert/strict";
import cytoscape from "cytoscape";
import { create } from "./adapter.mjs";

test("native remove twice emits once per removed element and restores the edge", () => {
  const cy = cytoscape({ headless: true, elements: [
    { data: { id: "a" } }, { data: { id: "b" } },
    { data: { id: "ab", source: "a", target: "b" } },
  ] });
  let removals = 0;
  cy.on("remove", () => removals++);
  const removed = cy.getElementById("a").remove();
  removed.remove();
  assert.equal(removals, 2);
  assert.deepEqual(cy.elements().map(e => e.id()), ["b"]);
  removed.restore();
  assert.equal(cy.getElementById("ab").source().id(), "a");
  assert.equal(cy.getElementById("ab").target().id(), "b");
  cy.destroy();
});

test("adapter rejects uninitialised and unknown events and resets its observation counters", () => {
  const adapter = create();
  assert.throws(() => adapter.step({ op: "remove", id: "a" }), /new must/);
  adapter.step({ op: "new" });
  assert.throws(() => adapter.step({ op: "invented" }), /unsupported/);
  assert.throws(() => adapter.step({ op: "select", id: "a", expect: {} }), /fields/);
  adapter.step({ op: "remove", id: "a" });
  assert.deepEqual(adapter.step({ op: "new" }).events, { add: 0, remove: 0, select: 0 });
  adapter.close();
});
