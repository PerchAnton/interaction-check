import test from "node:test";
import assert from "node:assert/strict";
import {create} from "./adapter.mjs";
import {fixture} from './adapter.mjs';
import {nextTick} from 'vue';
test('mounted useForm validates then resets its values and errors', async () => {
  const {form,app}=fixture();
  try {
    form.setFieldValue('name','',false); await form.validate();
    assert.equal(form.errors.value.name,'Required');
    form.resetForm(); await nextTick();
    assert.equal(form.values.name,'original'); assert.deepEqual(form.errors.value,{});
  } finally { app.unmount(); }
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
