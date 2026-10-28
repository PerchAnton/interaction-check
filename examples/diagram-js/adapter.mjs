import { Injector } from "didi";
import EventBus from "diagram-js/lib/core/EventBus.js";
import commandModule from "diagram-js/lib/command/index.js";
import { fields, index } from "../xstate/protocol.mjs";

export function fixture() {
  const injector = new Injector([commandModule, { eventBus: ["type", EventBus] }]);
  const stack = injector.get("commandStack");
  const model = { id: "example", value: 0 };
  const events = [];
  injector.get("eventBus").on("commandStack.changed", event => events.push(event.trigger));
  stack.register("value.set", {
    execute(context) { context.before = model.value; model.value = context.value; return [model]; },
    revert(context) { model.value = context.before; return [model]; },
    canExecute(context) { return context.value <= 10; },
  });
  return { stack, model, events };
}
export function create() {
  let host;
  let allowed = null;
  return {
    step(event) {
      if (event.op === "new") { fields(event, ["op"]); host = fixture(); allowed = null; }
      else {
        if (!host) throw new Error("new must be first");
        switch (event.op) {
          case "set": {
            fields(event, ["op", "value"]);
            const context = { value: index(event.value) };
            allowed = host.stack.canExecute("value.set", context);
            // CommandStack.execute does not call canExecute. The caller owns this gate.
            if (allowed) host.stack.execute("value.set", context);
            break;
          }
          case "undo": fields(event, ["op"]); host.stack.undo(); break;
          case "redo": fields(event, ["op"]); host.stack.redo(); break;
          case "clear": fields(event, ["op"]); host.stack.clear(); break;
          default: throw new Error("unsupported operation");
        }
      }
      return { value: host.model.value, undo: !!host.stack.canUndo(), redo: !!host.stack.canRedo(), allowed, events: [...host.events] };
    }, close() {},
  };
}
