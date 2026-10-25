import { createMachine, createActor, assign } from "xstate";
import { fields, text, choice } from "../protocol.mjs";

const machine = createMachine({
  id: "draft",
  initial: "idle",
  context: { saved: "original", draft: "original" },
  states: {
    idle: {
      on: {
        EDIT: {
          target: "editing",
          actions: assign({ draft: ({ context }) => context.saved }),
        },
      },
    },
    editing: {
      on: {
        CHANGE: { actions: assign({ draft: ({ event }) => event.value }) },
        CANCEL: "idle",
        SAVE: {
          target: "idle",
          guard: ({ context }) => context.draft.trim().length > 0,
          actions: assign({ saved: ({ context }) => context.draft }),
        },
      },
    },
  },
});

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
