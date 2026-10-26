import { createStore } from "zustand/vanilla";
import { subscribeWithSelector } from "zustand/middleware";
import { fields, text } from "../protocol.mjs";

export function create() {
  let store,
    unsubscribe,
    notifications = [];
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op", "title"]);
        unsubscribe?.();
        notifications = [];
        store = createStore(
          subscribeWithSelector(() => ({
            title: text(event.title),
            saved: false,
          })),
        );
        unsubscribe = store.subscribe(
          (s) => s.title,
          (value, previous) => notifications.push({ value, previous }),
        );
      } else {
        if (!store) throw new Error("new must be first");
        switch (event.op) {
          case "title":
            fields(event, ["op", "value"]);
            store.setState({ title: text(event.value) });
            break;
          case "saved":
            fields(event, ["op"]);
            store.setState({ saved: true });
            break;
          case "same":
            fields(event, ["op"]);
            store.setState(store.getState());
            break;
          case "replace":
            fields(event, ["op", "value"]);
            store.setState({ title: text(event.value) }, true);
            break;
          case "unsubscribe":
            fields(event, ["op"]);
            unsubscribe();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        value: store.getState(),
        keys: Object.keys(store.getState()).sort(),
        initial: store.getInitialState(),
        notifications,
      };
    },
    close() {
      unsubscribe?.();
    },
  };
}
