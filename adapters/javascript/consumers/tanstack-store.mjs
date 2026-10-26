import { createStore, batch } from "@tanstack/store";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let left,
    right,
    useLeft,
    selected,
    subscription,
    seen = [];
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "left", "right"]);
        const l = text(e.left),
          r = text(e.right);
        subscription?.unsubscribe();
        seen = [];
        left = createStore(l);
        right = createStore(r);
        useLeft = createStore(true);
        selected = createStore(() =>
          useLeft.state ? left.state : right.state,
        );
        subscription = selected.subscribe((value) => seen.push(value));
      } else {
        if (!selected) throw new Error("new must be first");
        switch (e.op) {
          case "set":
            fields(e, ["op", "side", "value"]);
            (choice(e.side, ["left", "right"]) === "left"
              ? left
              : right
            ).setState(() => text(e.value));
            break;
          case "select":
            fields(e, ["op", "side"]);
            {
              const side = choice(e.side, ["left", "right"]);
              useLeft.setState(() => side === "left");
            }
            break;
          case "batch": {
            fields(e, ["op", "left", "right"]);
            const l = text(e.left),
              r = text(e.right);
            batch(() => {
              left.setState(() => l);
              right.setState(() => r);
            });
            break;
          }
          case "unsubscribe":
            fields(e, ["op"]);
            subscription.unsubscribe();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        left: left.state,
        right: right.state,
        selected: selected.state,
        seen: [...seen],
      };
    },
    close() {
      subscription?.unsubscribe();
    },
  };
}
