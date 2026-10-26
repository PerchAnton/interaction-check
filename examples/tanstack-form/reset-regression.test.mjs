import test from "node:test";
import assert from "node:assert/strict";
import { FormApi } from "@tanstack/form-core";

test("reset must not be overwritten by a validation response for old values", async () => {
  let started;
  let resolveValidation;
  const waiting = new Promise(resolve => { started = resolve; });
  const form = new FormApi({
    defaultValues: { name: "original" },
    validators: {
      onChangeAsync: () => {
        started();
        return new Promise(resolve => { resolveValidation = resolve; });
      },
    },
  });
  const unmount = form.mount();
  try {
    form.setFieldValue("name", "edited");
    const pending = form.validate("change");
    await waiting;
    form.reset();
    resolveValidation("error for the old value");
    await pending;
    assert.deepEqual(form.state.values, { name: "original" });
    assert.deepEqual(form.state.errors, []);
  } finally { unmount(); }
});
