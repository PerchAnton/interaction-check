import { proxy, snapshot, subscribe } from "valtio/vanilla";
import { fields, text } from "../protocol.mjs";
export function create() {
  let state,
    initial,
    previous,
    stop,
    notifications = 0;
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "name"]);
        const name = text(e.name);
        stop?.();
        notifications = 0;
        state = proxy({ profile: { name }, saved: false });
        initial = snapshot(state);
        previous = initial;
        stop = subscribe(state, () => notifications++, true);
      } else {
        if (!state) throw new Error("new must be first");
        switch (e.op) {
          case "name":
            fields(e, ["op", "value"]);
            state.profile.name = text(e.value);
            break;
          case "replace":
            fields(e, ["op", "value"]);
            state.profile = { name: text(e.value) };
            break;
          case "save":
            fields(e, ["op"]);
            state.saved = true;
            break;
          case "unsubscribe":
            fields(e, ["op"]);
            stop();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      const current = snapshot(state),
        same = current === previous;
      previous = current;
      return { current, initial, same, notifications };
    },
    close() {
      stop?.();
    },
  };
}
