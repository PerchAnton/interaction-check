import { signal, computed, effect, batch } from "@preact/signals-core";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let left,
    right,
    useLeft,
    selected,
    stop,
    seen = [];
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "left", "right"]);
        const l = text(e.left),
          r = text(e.right);
        stop?.();
        seen = [];
        left = signal(l);
        right = signal(r);
        useLeft = signal(true);
        selected = computed(() => (useLeft.value ? left.value : right.value));
        stop = effect(() => {
          seen.push(selected.value);
        });
      } else {
        if (!selected) throw new Error("new must be first");
        switch (e.op) {
          case "set":
            fields(e, ["op", "side", "value"]);
            (choice(e.side, ["left", "right"]) === "left"
              ? left
              : right
            ).value = text(e.value);
            break;
          case "select":
            fields(e, ["op", "side"]);
            useLeft.value = choice(e.side, ["left", "right"]) === "left";
            break;
          case "batch": {
            fields(e, ["op", "left", "right", "side"]);
            const l = text(e.left),
              r = text(e.right),
              side = choice(e.side, ["left", "right"]);
            batch(() => {
              left.value = l;
              right.value = r;
              useLeft.value = side === "left";
            });
            break;
          }
          case "stop":
            fields(e, ["op"]);
            stop();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return { selected: selected.value, seen: [...seen] };
    },
    close() {
      stop?.();
    },
  };
}
