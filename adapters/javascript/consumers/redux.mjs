import { legacy_createStore, combineReducers, applyMiddleware } from "redux";
import { fields, text, index } from "../protocol.mjs";
export function create() {
  let store,
    unsubscribe,
    seen = [],
    order = [];
  const count = (s = 0, a) => (a.type === "set" ? a.value : s);
  const title = (s = "", a) => (a.type === "title" ? a.value : s);
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op"]);
        unsubscribe?.();
        seen = [];
        order = [];
        const monitor = (api) => (next) => (action) => {
          order.push("before:" + api.getState().count);
          const result = next(action);
          order.push("after:" + api.getState().count);
          return result;
        };
        store = legacy_createStore(
          combineReducers({ count, title }),
          applyMiddleware(monitor),
        );
        unsubscribe = store.subscribe(() => seen.push({ ...store.getState() }));
      } else {
        if (!store) throw new Error("new must be first");
        switch (e.op) {
          case "set":
            fields(e, ["op", "value"]);
            store.dispatch({ type: "set", value: index(e.value) });
            break;
          case "title":
            fields(e, ["op", "value"]);
            store.dispatch({ type: "title", value: text(e.value) });
            break;
          case "noop":
            fields(e, ["op"]);
            store.dispatch({ type: "noop" });
            break;
          case "unsubscribe":
            fields(e, ["op"]);
            unsubscribe();
            break;
          case "replace":
            fields(e, ["op"]);
            store.replaceReducer(
              combineReducers({ count, title, ready: (s = true) => s }),
            );
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return { value: store.getState(), seen: [...seen], order: [...order] };
    },
    close() {
      unsubscribe?.();
    },
  };
}
