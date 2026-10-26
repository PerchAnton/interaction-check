import { atom, createStore } from "jotai/vanilla";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let value,
    upper,
    stores,
    stops = {},
    seen;
  const close = () => Object.values(stops).forEach((stop) => stop());
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "value"]);
        const initial = text(e.value);
        close();
        seen = { a: [], b: [] };
        stops = {};
        value = atom(initial);
        upper = atom((get) => get(value).toUpperCase());
        stores = { a: createStore(), b: createStore() };
        for (const id of ["a", "b"])
          stops[id] = stores[id].sub(upper, () =>
            seen[id].push(stores[id].get(upper)),
          );
      } else {
        if (!stores) throw new Error("new must be first");
        switch (e.op) {
          case "set":
            fields(e, ["op", "store", "value"]);
            stores[choice(e.store, ["a", "b"])].set(value, text(e.value));
            break;
          case "unsubscribe":
            fields(e, ["op", "store"]);
            stops[choice(e.store, ["a", "b"])]();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        a: stores.a.get(upper),
        b: stores.b.get(upper),
        seen: { a: [...seen.a], b: [...seen.b] },
      };
    },
    close,
  };
}
