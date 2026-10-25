import test from "node:test";
import assert from "node:assert/strict";

// A bad final argument must not leave a partly applied transaction in a live adapter.
for (const [name, initial, invalid, probe] of [
  [
    "mobx",
    { op: "new", first: "A", last: "B" },
    { op: "rename", first: "changed", last: null },
    { op: "dispose" },
  ],
  [
    "nanostores",
    { op: "new", title: "A" },
    { op: "batch", title: "changed", done: "true" },
    { op: "unsubscribe" },
  ],
  [
    "pinia",
    { op: "new", title: "A" },
    { op: "patch", title: "changed", saved: true, mode: "unknown" },
    { op: "unsubscribe" },
  ],
  [
    "final-form",
    { op: "new", title: "A" },
    { op: "batch", first: "changed", last: null },
    { op: "focus" },
  ],
  [
    "tanstack-store",
    { op: "new", left: "A", right: "B" },
    { op: "batch", left: "changed", right: null },
    { op: "unsubscribe" },
  ],
]) {
  test(`${name}: invalid batch leaves values and notifications unchanged`, async () => {
    const { create } = await import(`../consumers/${name}.mjs`);
    const adapter = create();
    try {
      const before = structuredClone(await adapter.step(initial));
      await assert.rejects(async () => adapter.step(invalid));
      assert.deepEqual(await adapter.step(probe), before);
    } finally {
      adapter.close?.();
    }
  });
}
