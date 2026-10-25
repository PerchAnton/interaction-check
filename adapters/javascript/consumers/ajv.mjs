import { validationState } from "../validation-state.mjs";
import Ajv from "ajv";
import { fields, choice } from "../protocol.mjs";
const schema = {
  type: "object",
  required: ["name", "age"],
  additionalProperties: false,
  properties: {
    name: { type: "string", minLength: 1 },
    age: { type: "integer", minimum: 0 },
    enabled: { type: "boolean", default: true },
  },
};
export function create() {
  const validators = Object.fromEntries(
    [false, true].map((coerceTypes) => [
      String(coerceTypes),
      new Ajv({ allErrors: true, useDefaults: true, coerceTypes }).compile(
        schema,
      ),
    ]),
  );
  return {
    step(e) {
      fields(e, ["op", "data", "coerce"]);
      if (e.op !== "validate") throw new Error("unsupported operation");
      const coerce = choice(e.coerce, [true, false]),
        input = structuredClone(e.data),
        output = structuredClone(e.data),
        validate = validators[String(coerce)];
      const valid = validate(output);
      return validationState({
        valid,
        output,
        paths: (validate.errors ?? [])
          .map(
            (x) =>
              x.instancePath +
              (x.keyword === "required"
                ? "/" + x.params.missingProperty
                : x.keyword === "additionalProperties"
                  ? "/" + x.params.additionalProperty
                  : ""),
          )
          .sort(),
        input,
        after: e.data,
      });
    },
  };
}
