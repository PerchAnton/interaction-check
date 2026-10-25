import {
  createStore,
  createEvent,
  fork,
  allSettled,
  serialize,
} from "effector";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let store, upper, change, reset, scopes;
  return {
    async step(e) {
      if (e.op === "new") {
        fields(e, ["op", "value"]);
        const initial = text(e.value);
        change = createEvent();
        reset = createEvent();
        store = createStore(initial, { sid: "title" })
          .on(change, (_, value) => value)
          .reset(reset);
        upper = store.map((value) => value.toUpperCase());
        scopes = { a: fork(), b: fork() };
      } else {
        if (!scopes) throw new Error("new must be first");
        switch (e.op) {
          case "set":
            fields(e, ["op", "scope", "value"]);
            await allSettled(change, {
              scope: scopes[choice(e.scope, ["a", "b"])],
              params: text(e.value),
            });
            break;
          case "reset":
            fields(e, ["op", "scope"]);
            await allSettled(reset, {
              scope: scopes[choice(e.scope, ["a", "b"])],
            });
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        root: store.getState(),
        a: scopes.a.getState(upper),
        b: scopes.b.getState(upper),
        serialized: { a: serialize(scopes.a), b: serialize(scopes.b) },
      };
    },
  };
}
