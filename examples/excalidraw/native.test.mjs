import test from "node:test";
import assert from "node:assert/strict";
import { core, fixture, create } from "./adapter.mjs";

test("real mutateElement preserves version for no-op and restore retains saved geometry", () => {
  const elements = fixture();
  const saved = JSON.stringify(elements);
  const version = elements[0].version;
  core.mutateElement(elements[0], { x: 10, y: 20 });
  assert.equal(elements[0].version, version);
  core.mutateElement(elements[0], { x: 50 });
  assert.equal(elements[0].version, version + 1);
  const restored = core.restoreElements(JSON.parse(saved), null, { repairBindings: true });
  assert.equal(restored[0].x, 10);
  assert.equal(restored[0].id, "a");
});

test("adapter rejects missing initialization, expectations, and unknown operations", () => {
  const adapter = create();
  try {
    assert.throws(() => adapter.step({ op: "move", x: 0, y: 0 }));
    assert.throws(() => adapter.step({ op: "new", expect: {} }));
    adapter.step({ op: "new" });
    assert.throws(() => adapter.step({ op: "unknown" }));
    assert.throws(() => adapter.step({ op: "restore" }));
  } finally { adapter.close(); }
});
