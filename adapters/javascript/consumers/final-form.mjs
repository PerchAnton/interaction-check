import { createForm } from "final-form";
import { fields, text } from "../protocol.mjs";
export function create() {
  let form,
    stopField,
    stopForm,
    valuesSeen = [],
    submissions = [];
  const close = () => {
    stopForm?.();
    stopField?.();
  };
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "title"]);
        const title = text(e.title);
        close();
        valuesSeen = [];
        submissions = [];
        form = createForm({
          initialValues: { title },
          onSubmit: (values) => {
            submissions.push({ ...values });
          },
          validate: (values) =>
            values.title.trim() ? {} : { title: "Required" },
        });
        stopField = form.registerField("title", () => {}, {
          value: true,
          touched: true,
        });
        stopForm = form.subscribe(
          (state) => valuesSeen.push({ ...state.values }),
          { values: true },
        );
      } else {
        if (!form) throw new Error("new must be first");
        switch (e.op) {
          case "change":
            fields(e, ["op", "value"]);
            form.change("title", text(e.value));
            break;
          case "focus":
            fields(e, ["op"]);
            form.focus("title");
            break;
          case "blur":
            fields(e, ["op"]);
            form.blur("title");
            break;
          case "reset":
            fields(e, ["op"]);
            form.reset();
            break;
          case "restart":
            fields(e, ["op"]);
            form.restart();
            break;
          case "submit":
            fields(e, ["op"]);
            form.submit();
            break;
          case "batch": {
            fields(e, ["op", "first", "last"]);
            const first = text(e.first),
              last = text(e.last);
            form.batch(() => {
              form.change("title", first);
              form.change("title", last);
            });
            break;
          }
          default:
            throw new Error("unsupported operation");
        }
      }
      const s = form.getState();
      return {
        values: { ...s.values },
        pristine: s.pristine,
        valid: s.valid,
        touched: form.getFieldState("title").touched,
        submitSucceeded: s.submitSucceeded,
        submissions: [...submissions],
        valuesSeen: [...valuesSeen],
      };
    },
    close,
  };
}
