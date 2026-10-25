import { writable, derived, get } from "svelte/store";
import { fields, text } from "../protocol.mjs";
export function create() {
  let store,
    upper,
    stop,
    seen = [];
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "title"]);
        const title = text(e.title);
        stop?.();
        seen = [];
        store = writable({ title, saved: false });
        upper = derived(store, (s) => s.title.toUpperCase());
        stop = store.subscribe((value) => seen.push({ ...value }));
      } else {
        if (!store) throw new Error("new must be first");
        switch (e.op) {
          case "title":
            fields(e, ["op", "value"]);
            {
              const title = text(e.value);
              store.update((s) => ({ ...s, title }));
            }
            break;
          case "save":
            fields(e, ["op"]);
            store.update((s) => ({ ...s, saved: true }));
            break;
          case "same":
            fields(e, ["op"]);
            store.set(get(store));
            break;
          case "unsubscribe":
            fields(e, ["op"]);
            stop();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return { value: { ...get(store) }, upper: get(upper), seen: [...seen] };
    },
    close() {
      stop?.();
    },
  };
}
