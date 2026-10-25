import { validationState } from "../validation-state.mjs";
import * as yup from "yup";
import { fields, choice } from "../protocol.mjs";
const schema = yup.object({
  name: yup.string().trim().required(),
  age: yup.number().integer().min(0).required(),
  enabled: yup.boolean().default(true),
});
export function create() {
  return {
    step(e) {
      fields(e, ["op", "data", "mode"]);
      if (e.op !== "validate") throw new Error("unsupported operation");
      const mode = choice(e.mode, ["cast", "strict"]),
        input = structuredClone(e.data);
      try {
        return validationState({
          valid: true,
          output: schema.validateSync(e.data, {
            strict: mode === "strict",
            abortEarly: false,
            stripUnknown: true,
          }),
          paths: [],
          input,
          after: e.data,
        });
      } catch (error) {
        if (!(error instanceof yup.ValidationError)) throw error;
        return validationState({
          valid: false,
          output: null,
          paths: error.inner.map((x) => x.path ?? "").sort(),
          input,
          after: e.data,
        });
      }
    },
  };
}
