import { reactive, computed, effect, effectScope } from "@vue/reactivity";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let state,
    selected,
    scope,
    seen = [];
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "left", "right"]);
        const left = text(e.left),
          right = text(e.right);
        scope?.stop();
        seen = [];
        state = reactive({ left, right, useLeft: true });
        selected = computed(() => (state.useLeft ? state.left : state.right));
        scope = effectScope();
        scope.run(() => effect(() => seen.push(selected.value)));
      } else {
        if (!state) throw new Error("new must be first");
        switch (e.op) {
          case "set":
            fields(e, ["op", "field", "value"]);
            state[choice(e.field, ["left", "right"])] = text(e.value);
            break;
          case "select":
            fields(e, ["op", "side"]);
            state.useLeft = choice(e.side, ["left", "right"]) === "left";
            break;
          case "stop":
            fields(e, ["op"]);
            scope.stop();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return { selected: selected.value, seen: [...seen] };
    },
    close() {
      scope?.stop();
    },
  };
}
