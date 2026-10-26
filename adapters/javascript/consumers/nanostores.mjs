import { map, batch } from "nanostores";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let store,
    stop,
    seen = [];
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "title"]);
        const title = text(e.title);
        stop?.();
        seen = [];
        store = map({ title, done: false });
        stop = store.listen((value) => seen.push({ ...value }));
      } else {
        if (!store) throw new Error("new must be first");
        switch (e.op) {
          case "title":
            fields(e, ["op", "value"]);
            store.setKey("title", text(e.value));
            break;
          case "done":
            fields(e, ["op", "value"]);
            store.setKey("done", choice(e.value, [true, false]));
            break;
          case "batch": {
            fields(e, ["op", "title", "done"]);
            const title = text(e.title),
              done = choice(e.done, [true, false]);
            batch(() => {
              store.setKey("title", title);
              store.setKey("done", done);
            });
            break;
          }
          case "unsubscribe":
            fields(e, ["op"]);
            stop();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return { value: { ...store.get() }, seen: [...seen] };
    },
    close() {
      stop?.();
    },
  };
}
