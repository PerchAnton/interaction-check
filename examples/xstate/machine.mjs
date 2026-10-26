import { createMachine, assign } from "xstate";

export const machine = createMachine({
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

