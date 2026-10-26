import { create as suiteCreate, enforce, test } from "vest";
import { fields, text, index, choice } from "../protocol.mjs";
export function create() {
  let suite, result;
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op"]);
        suite = suiteCreate((data) => {
          test("name", "Required", () => enforce(data.name).isNotBlank());
          test("age", "Adult only", () =>
            enforce(data.age).greaterThanOrEquals(18),
          );
        });
        result = suite.get();
      } else {
        if (!suite) throw new Error("new must be first");
        switch (e.op) {
          case "run": {
            fields(e, ["op", "name", "age", "only"]);
            const name = text(e.name),
              age = index(e.age, 120),
              only = choice(e.only, ["all", "name", "age"]);
            result = (only === "all" ? suite : suite.only(only)).run({
              name,
              age,
            });
            break;
          }
          case "reset":
            fields(e, ["op"]);
            suite.reset();
            result = suite.get();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        valid: result.isValid(),
        errors: result.getErrors(),
        errorFields: Object.keys(result.getErrors()).sort(),
        errorCount: result.errorCount,
        testCount: result.testCount,
      };
    },
  };
}
