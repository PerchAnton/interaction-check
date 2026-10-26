import test from "node:test";
import assert from "node:assert/strict";
import { FormApi } from "@tanstack/form-core";
import { create } from "./adapter.mjs";

test("normal form validation applies its error; reset clears completed validation", async () => {
  const form = new FormApi({ defaultValues: { name: "original" }, validators: {
    onChangeAsync: async () => "invalid",
  } });
  const unmount = form.mount();
  try {
    form.setFieldValue("name", "edited");
    await form.validate("change");
    assert.deepEqual(form.state.errors, ["invalid"]);
    form.reset();
    assert.deepEqual(form.state.errors, []);
    assert.deepEqual(form.state.values, { name: "original" });
  } finally { unmount(); }
});

test("adapter rejects expectations and unknown operations", async () => {
  const adapter = create();
  try {
    await assert.rejects(adapter.step({ op: "reset" }));
    await assert.rejects(adapter.step({ op: "new", expect: {} }));
    await adapter.step({ op: "new" });
    await assert.rejects(adapter.step({ op: "invented" }));
    await assert.rejects(adapter.step({ op: "resolve", error: null }));
  } finally { await adapter.close(); }
});
