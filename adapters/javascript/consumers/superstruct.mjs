import { validationState } from "../validation-state.mjs";
import {
  object,
  string,
  integer,
  boolean,
  defaulted,
  min,
  size,
  coerce,
  create as parse,
  mask,
  StructError,
} from "superstruct";
import { fields, choice } from "../protocol.mjs";
const schema = object({
  name: coerce(size(string(), 1, 4096), string(), (value) => value.trim()),
  age: min(integer(), 0),
  enabled: defaulted(boolean(), true),
});
export function create() {
  return {
    step(e) {
      fields(e, ["op", "data", "mode"]);
      if (e.op !== "validate") throw new Error("unsupported operation");
      const mode = choice(e.mode, ["create", "mask"]),
        input = structuredClone(e.data);
      try {
        return validationState({
          valid: true,
          output: (mode === "mask" ? mask : parse)(e.data, schema),
          paths: [],
          input,
          after: e.data,
        });
      } catch (error) {
        if (!(error instanceof StructError)) throw error;
        return validationState({
          valid: false,
          output: null,
          paths: error
            .failures()
            .map((x) => x.path.join("."))
            .sort(),
          input,
          after: e.data,
        });
      }
    },
  };
}
