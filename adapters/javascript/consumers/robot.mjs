import {
  createMachine,
  state,
  transition,
  guard,
  reduce,
  interpret,
} from "robot3";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let service;
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "value"]);
        const value = text(e.value);
        const machine = createMachine(
          {
            idle: state(
              transition(
                "edit",
                "editing",
                reduce((c) => ({ ...c, draft: c.value })),
              ),
            ),
            editing: state(
              transition(
                "input",
                "editing",
                reduce((c, e) => ({ ...c, draft: e.value })),
              ),
              transition(
                "save",
                "idle",
                guard((c) => c.draft.trim().length > 0),
                reduce((c) => ({ ...c, value: c.draft })),
              ),
              transition(
                "cancel",
                "idle",
                reduce((c) => ({ ...c, draft: c.value })),
              ),
            ),
          },
          () => ({ value, draft: value }),
        );
        service = interpret(machine, () => {});
      } else {
        if (!service) throw new Error("new must be first");
        if (e.op === "input") {
          fields(e, ["op", "value"]);
          service.send({ type: "input", value: text(e.value) });
        } else {
          fields(e, ["op"]);
          service.send(choice(e.op, ["edit", "save", "cancel"]));
        }
      }
      return { state: service.machine.current, ...service.context };
    },
  };
}
