import { validationState } from "../validation-state.mjs";
import Joi from "joi";
import { fields, choice } from "../protocol.mjs";
const schema = Joi.object({
  name: Joi.string().trim().required(),
  age: Joi.number().integer().min(0).required(),
  enabled: Joi.boolean().default(true),
});
export function create() {
  return {
    step(e) {
      fields(e, ["op", "data", "convert"]);
      if (e.op !== "validate") throw new Error("unsupported operation");
      const convert = choice(e.convert, [true, false]),
        input = structuredClone(e.data),
        parsed = schema.validate(e.data, {
          convert,
          abortEarly: false,
          stripUnknown: true,
        });
      return validationState({
        valid: !parsed.error,
        output: parsed.error ? null : parsed.value,
        paths: parsed.error
          ? parsed.error.details.map((x) => x.path.join(".")).sort()
          : [],
        input,
        after: e.data,
      });
    },
  };
}
