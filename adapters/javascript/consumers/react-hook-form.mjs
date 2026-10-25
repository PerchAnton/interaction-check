import { createFormControl } from "react-hook-form";
import { fields, text } from "../protocol.mjs";
export function create() {
  let form,
    unsubscribe,
    submissions = [],
    invalidSubmits = 0,
    lastValid = null;
  return {
    async step(e) {
      if (e.op === "new") {
        fields(e, ["op", "title"]);
        const title = text(e.title);
        unsubscribe?.();
        submissions = [];
        invalidSubmits = 0;
        lastValid = null;
        form = createFormControl({ defaultValues: { title } });
        form.register("title", { required: true, minLength: 3 });
        unsubscribe = form.subscribe({
          formState: {
            values: true,
            isDirty: true,
            dirtyFields: true,
            touchedFields: true,
            errors: true,
          },
          callback: () => {},
        });
      } else {
        if (!form) throw new Error("new must be first");
        switch (e.op) {
          case "input":
            fields(e, ["op", "value"]);
            form.setValue("title", text(e.value), {
              shouldDirty: true,
              shouldTouch: true,
            });
            break;
          case "validate":
            fields(e, ["op"]);
            lastValid = await form.trigger("title");
            break;
          case "reset":
            fields(e, ["op"]);
            form.reset();
            lastValid = null;
            break;
          case "submit":
            fields(e, ["op"]);
            await form.handleSubmit(
              (value) => {
                submissions.push({ ...value });
              },
              () => {
                invalidSubmits++;
              },
            )();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      const f = form.getFieldState("title");
      return {
        value: form.getValues("title"),
        dirty: f.isDirty,
        touched: f.isTouched,
        error: f.error?.type ?? null,
        lastValid,
        submissions: [...submissions],
        invalidSubmits,
      };
    },
    close() {
      unsubscribe?.();
    },
  };
}
