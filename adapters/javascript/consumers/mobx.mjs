import { observable, computed, autorun, runInAction } from "mobx";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let state,
    full,
    dispose,
    seen = [];
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "first", "last"]);
        const first = text(e.first),
          last = text(e.last);
        dispose?.();
        seen = [];
        state = observable({ first, last });
        full = computed(() => `${state.first} ${state.last}`);
        dispose = autorun(() => seen.push(full.get()));
      } else {
        if (!state) throw new Error("new must be first");
        switch (e.op) {
          case "set": {
            fields(e, ["op", "field", "value"]);
            const key = choice(e.field, ["first", "last"]),
              value = text(e.value);
            runInAction(() => {
              state[key] = value;
            });
            break;
          }
          case "rename": {
            fields(e, ["op", "first", "last"]);
            const first = text(e.first),
              last = text(e.last);
            runInAction(() => {
              state.first = first;
              state.last = last;
            });
            break;
          }
          case "dispose":
            fields(e, ["op"]);
            dispose();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return { full: full.get(), seen: [...seen] };
    },
    close() {
      dispose?.();
    },
  };
}
