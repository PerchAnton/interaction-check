import { validationState } from "../validation-state.mjs";
import { z } from "zod";
import { fields } from "../protocol.mjs";
const schema = z.object({
  name: z.string().trim().min(1),
  age: z.number().int().nonnegative(),
  enabled: z.boolean().default(true),
});
export function create() {
  return {
    step(e) {
      fields(e, ["op", "data"]);
      if (e.op !== "validate") throw new Error("unsupported operation");
      const input = structuredClone(e.data),
        parsed = schema.safeParse(e.data);
      return validationState({
        valid: parsed.success,
        output: parsed.success ? parsed.data : null,
        paths: parsed.success
          ? []
          : parsed.error.issues.map((x) => x.path.join(".")).sort(),
        input,
        after: e.data,
      });
    },
  };
}
