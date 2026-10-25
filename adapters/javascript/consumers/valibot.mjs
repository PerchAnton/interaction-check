import { validationState } from "../validation-state.mjs";
import * as v from "valibot";
import { fields } from "../protocol.mjs";
const schema = v.object({
  name: v.pipe(v.string(), v.trim(), v.minLength(1)),
  age: v.pipe(v.number(), v.integer(), v.minValue(0)),
  enabled: v.optional(v.boolean(), true),
});
export function create() {
  return {
    step(e) {
      fields(e, ["op", "data"]);
      if (e.op !== "validate") throw new Error("unsupported operation");
      const input = structuredClone(e.data),
        parsed = v.safeParse(schema, e.data);
      return validationState({
        valid: parsed.success,
        output: parsed.success ? parsed.output : null,
        paths: parsed.success
          ? []
          : parsed.issues
              .map((x) => (x.path ?? []).map((p) => p.key).join("."))
              .sort(),
        input,
        after: e.data,
      });
    },
  };
}
