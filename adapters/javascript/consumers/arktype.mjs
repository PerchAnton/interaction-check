import { validationState } from "../validation-state.mjs";
import { type } from "arktype";
import { fields } from "../protocol.mjs";
const schema = type({
  name: "string > 0",
  age: "number.integer >= 0",
  "enabled?": "boolean",
}).onUndeclaredKey("delete");
export function create() {
  return {
    step(e) {
      fields(e, ["op", "data"]);
      if (e.op !== "validate") throw new Error("unsupported operation");
      const input = structuredClone(e.data),
        parsed = schema(e.data),
        valid = !(parsed instanceof type.errors);
      return validationState({
        valid,
        output: valid ? parsed : null,
        paths: valid ? [] : [...parsed].map((x) => x.path.join(".")).sort(),
        input,
        after: e.data,
      });
    },
  };
}
