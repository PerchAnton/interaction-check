import { NodeEditor } from "rete";
import { fields, text, choice } from "../xstate/protocol.mjs";

export function create() {
  let editor;
  let blocked;
  let result = null;
  let events = [];
  return {
    async step(event) {
      if (event.op === "new") {
        fields(event, ["op"]);
        editor = new NodeEditor();
        blocked = undefined;
        events = [];
        result = null;
        editor.addPipe(context => {
          events.push(context.type);
          if (context.type === blocked) return undefined;
          return context;
        });
      } else {
        if (!editor) throw new Error("new must be first");
        switch (event.op) {
          case "block":
            fields(event, ["op", "signal"]);
            blocked = choice(event.signal, ["noderemove", "connectioncreate", "clear", null]);
            result = null;
            break;
          case "add_node":
            fields(event, ["op", "id"]);
            result = await editor.addNode({ id: text(event.id) });
            break;
          case "add_edge":
            fields(event, ["op", "id", "source", "target"]);
            result = await editor.addConnection({ id: text(event.id), source: text(event.source), target: text(event.target) });
            break;
          case "remove_node":
            fields(event, ["op", "id"]);
            result = await editor.removeNode(text(event.id));
            break;
          case "clear":
            fields(event, ["op"]);
            result = await editor.clear();
            break;
          default: throw new Error("unsupported operation");
        }
      }
      return { nodes: editor.getNodes().map(n => n.id).sort(), edges: editor.getConnections().map(e => e.id).sort(), result, events: [...events] };
    },
    close() {},
  };
}
