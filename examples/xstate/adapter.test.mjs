import { test } from "node:test";
import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { create } from "./adapter.mjs";

test("reject unsupported operations, missing setup and invalid CHANGE input", () => {
  for (const event of [{ op: "restore" }, { op: "send", type: "EDIT" }, { op: "unknown" }]) {
    const adapter = create();
    try { assert.throws(() => adapter.step(event)); } finally { adapter.close(); }
  }
  const adapter = create();
  try {
    adapter.step({ op: "new" });
    assert.throws(() => adapter.step({ op: "send", type: "CHANGE", value: 3 }));
    assert.throws(() => adapter.step({ op: "new", expect: {} }));
  } finally { adapter.close(); }
});

test("new clears the checkpoint and actors do not leak across examples", () => {
  const adapter = create();
  try {
    adapter.step({ op: "new" });
    adapter.step({ op: "checkpoint" });
    adapter.step({ op: "new" });
    assert.throws(() => adapter.step({ op: "restore" }));
  } finally { adapter.close(); }
});

test("bounded protocol rejects extra fields, invalid UTF-8 and oversized records", () => {
  const path = fileURLToPath(new URL("./main.mjs", import.meta.url));
  for (const input of [
    '{"protocol":1,"id":1,"event":{"op":"new"},"expect":{}}\n',
    Buffer.from([255, 10]),
    "x".repeat(65537),
  ]) {
    const result = spawnSync(process.execPath, [path], { input, encoding: "utf8", timeout: 5000 });
    assert.equal(result.status, 1);
    assert.notEqual(result.stderr.trim(), "");
    assert.equal(result.stdout, "");
  }
});
