import { createRenderer, nextTick } from "vue";
import { useForm } from "vee-validate";
import { fields, text } from "../xstate/protocol.mjs";
// A null-rendering component supplies actual Vue setup/mount/unmount lifecycles.
// This is a headless form-model test, not a browser or accessibility test.
const renderer = createRenderer({
  createComment: value => ({ value }), createText: value => ({ value }),
  createElement: tag => ({ tag }), insert() {}, remove() {},
  parentNode: () => null, nextSibling: () => null,
  setText(node, value) { node.value = value; }, setElementText() {}, patchProp() {},
});
export function fixture() {
  let form;
  const app = renderer.createApp({ setup() {
    form = useForm({ initialValues: { name: "original" }, validationSchema: {
      name: value => value.trim() ? true : "Required",
    } });
    return () => null;
  } });
  app.mount({});
  return { form, app };
}
export function create() {
  let host;
  return {
    async step(event) {
      if (event.op === "new") { fields(event, ["op"]); host?.app.unmount(); host = fixture(); }
      else {
        if (!host) throw new Error("new must be first");
        switch (event.op) {
          case "set": fields(event, ["op", "value"]); host.form.setFieldValue("name", text(event.value), false); break;
          case "validate": fields(event, ["op"]); await host.form.validate(); break;
          case "reset": fields(event, ["op"]); host.form.resetForm(); break;
          default: throw new Error("unsupported operation");
        }
      }
      await nextTick();
      return { values: { ...host.form.values }, errors: { ...host.form.errors.value },
        error_names: Object.keys(host.form.errors.value).sort(), dirty: host.form.meta.value.dirty };
    }, close() { host?.app.unmount(); },
  };
}
