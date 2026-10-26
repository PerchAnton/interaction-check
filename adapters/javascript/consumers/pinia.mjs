import { createPinia, defineStore, disposePinia } from "pinia";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let pinia,
    otherPinia,
    store,
    other,
    stop,
    seen = [];
  const close = () => {
    stop?.();
    if (pinia) disposePinia(pinia);
    if (otherPinia) disposePinia(otherPinia);
  };
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "title"]);
        const title = text(e.title);
        close();
        seen = [];
        pinia = createPinia();
        otherPinia = createPinia();
        const useDraft = defineStore("draft", {
          state: () => ({ title, saved: false }),
        });
        store = useDraft(pinia);
        other = useDraft(otherPinia);
        stop = store.$subscribe(
          (mutation, state) =>
            seen.push({
              type: mutation.type,
              title: state.title,
              saved: state.saved,
            }),
          { flush: "sync", detached: true },
        );
      } else {
        if (!store) throw new Error("new must be first");
        switch (e.op) {
          case "title":
            fields(e, ["op", "value"]);
            store.title = text(e.value);
            break;
          case "patch": {
            fields(e, ["op", "title", "saved", "mode"]);
            const title = text(e.title),
              saved = choice(e.saved, [true, false]),
              mode = choice(e.mode, ["object", "function"]);
            if (mode === "object") store.$patch({ title, saved });
            else
              store.$patch((state) => {
                state.title = title;
                state.saved = saved;
              });
            break;
          }
          case "reset":
            fields(e, ["op"]);
            store.$reset();
            break;
          case "unsubscribe":
            fields(e, ["op"]);
            stop();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        value: { ...store.$state },
        other: { ...other.$state },
        seen: [...seen],
      };
    },
    close,
  };
}
