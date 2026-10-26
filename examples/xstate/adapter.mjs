import { createActor } from "xstate";
import { machine } from "./machine.mjs";
import { fields, text, choice } from "./protocol.mjs";

export function create() {
  let actor, saved;
  const start = (snapshot) => {
    actor?.stop();
    actor = createActor(machine, { snapshot }).start();
  };
  return {
    step(event) {
      switch (event.op) {
        case "new":
          fields(event, ["op"]);
          saved = undefined;
          start();
          break;
        case "send":
          if (!actor) throw new Error("new must be first");
          fields(event, ["op", "type"], ["value"]);
          choice(event.type, ["EDIT", "CHANGE", "CANCEL", "SAVE"]);
          actor.send(
            event.type === "CHANGE"
              ? { type: "CHANGE", value: text(event.value) }
              : { type: event.type },
          );
          break;
        case "checkpoint":
          fields(event, ["op"]);
          if (!actor) throw new Error("new must be first");
          saved = JSON.parse(JSON.stringify(actor.getPersistedSnapshot()));
          break;
        case "restore":
          fields(event, ["op"]);
          if (!saved) throw new Error("checkpoint required");
          start(saved);
          break;
        default:
          throw new Error("unsupported operation");
      }
      const snapshot = actor.getSnapshot();
      return {
        value: snapshot.value,
        context: snapshot.context,
        status: snapshot.status,
        can_save: snapshot.can({ type: "SAVE" }),
      };
    },
    close() {
      actor?.stop();
    },
  };
}
