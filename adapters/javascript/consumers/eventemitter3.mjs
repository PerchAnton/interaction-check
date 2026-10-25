import EventEmitter from "eventemitter3";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let emitter,
    seen = [],
    regular,
    context,
    emitted = null;
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "reentrant"]);
        const reentrant = choice(e.reentrant, [true, false]);
        emitter?.removeAllListeners();
        emitter = new EventEmitter();
        seen = [];
        emitted = null;
        context = { label: "context" };
        regular = function (value) {
          seen.push({ listener: this.label, value });
        };
        emitter.on("data", regular, context);
        emitter.once("data", (value) => {
          seen.push({ listener: "once", value });
          if (reentrant) emitter.emit("data", value + "!");
        });
      } else {
        if (!emitter) throw new Error("new must be first");
        switch (e.op) {
          case "emit":
            fields(e, ["op", "value"]);
            emitted = emitter.emit("data", text(e.value));
            break;
          case "off":
            fields(e, ["op"]);
            emitter.removeListener("data", regular, context);
            break;
          case "clear":
            fields(e, ["op"]);
            emitter.removeAllListeners();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        seen: [...seen],
        listeners: emitter.listenerCount("data"),
        events: emitter.eventNames(),
        emitted,
      };
    },
    close() {
      emitter?.removeAllListeners();
    },
  };
}
