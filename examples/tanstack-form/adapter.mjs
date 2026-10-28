import { FormApi } from "@tanstack/form-core";
import { fields, text } from "../xstate/protocol.mjs";

export function create() {
  let form;
  let unmount;
  let pending;
  let release;
  let notify;
  return {
    async step(event) {
      if (event.op === "new") {
        fields(event, ["op"]);
        if (pending) throw new Error("settle validation before new");
        unmount?.();
        form = new FormApi({ defaultValues: { name: "original" }, validators: {
          onChangeAsync: () => { notify(); return new Promise(resolve => { release = resolve; }); },
        } });
        unmount = form.mount();
      } else {
        if (!form) throw new Error("new must be first");
        switch (event.op) {
          case "set": fields(event, ["op", "value"]); form.setFieldValue("name", text(event.value)); break;
          case "start": {
            fields(event, ["op"]);
            if (pending) throw new Error("one pending validation supported");
            const started = new Promise(resolve => { notify = resolve; });
            pending = form.validate("change");
            await started;
            break;
          }
          case "resolve": {
            fields(event, ["op", "error"]);
            if (!pending) throw new Error("start required");
            release(event.error === null ? undefined : text(event.error));
            await pending;
            pending = undefined;
            break;
          }
          case "reset": fields(event, ["op"]); form.reset(); break;
          default: throw new Error("unsupported operation");
        }
      }
      return { values: form.state.values, errors: form.state.errors,
        validating: form.state.isFormValidating, dirty: form.state.isDirty };
    },
    async close() { if (pending) { release(undefined); await pending; } unmount?.(); },
  };
}
