import { fromJS } from "immutable";
import { fields, text, index } from "../protocol.mjs";
export function create() {
  let current, initial, previous;
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "title"]);
        current = fromJS({ title: text(e.title), items: [] });
        initial = current;
        previous = current;
      } else {
        if (!current) throw new Error("new must be first");
        switch (e.op) {
          case "title":
            fields(e, ["op", "value"]);
            current = current.set("title", text(e.value));
            break;
          case "append":
            fields(e, ["op", "value"]);
            {
              const value = text(e.value);
              current = current.update("items", (items) => items.push(value));
            }
            break;
          case "replace":
            fields(e, ["op", "at", "value"]);
            {
              const at = index(e.at, current.get("items").size - 1),
                value = text(e.value);
              current = current.setIn(["items", at], value);
            }
            break;
          case "batch": {
            fields(e, ["op", "title", "item"]);
            const title = text(e.title),
              item = text(e.item);
            current = current.withMutations((draft) => {
              draft.set("title", title);
              draft.update("items", (items) => items.push(item));
            });
            break;
          }
          default:
            throw new Error("unsupported operation");
        }
      }
      const result = {
        value: current.toJS(),
        initial: initial.toJS(),
        same: current === previous,
        itemsShared: current.get("items") === previous.get("items"),
      };
      previous = current;
      return result;
    },
  };
}
