import { applyNodeChanges, applyEdgeChanges } from "@xyflow/react";
import { fields, text, index } from "../xstate/protocol.mjs";
export function create() {
  let nodes, edges;
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op"]);
        nodes = [{ id: "a", position: { x: 0, y: 0 }, data: { label: "A" } },
          { id: "b", position: { x: 100, y: 0 }, data: { label: "B" } }];
        edges = [{ id: "ab", source: "a", target: "b" }];
      } else {
        if (!nodes) throw new Error("new must be first");
        switch (event.op) {
          case "move":
            fields(event, ["op", "id", "x", "y"]);
            nodes = applyNodeChanges([{ type: "position", id: text(event.id), position: { x: index(event.x), y: index(event.y) }, dragging: true }], nodes);
            break;
          case "select":
            fields(event, ["op", "id"]);
            nodes = applyNodeChanges([{ type: "select", id: text(event.id), selected: true }], nodes);
            break;
          case "remove":
            fields(event, ["op", "id"]);
            nodes = applyNodeChanges([{ type: "remove", id: text(event.id) }], nodes);
            break;
          case "remove_edge":
            fields(event, ["op", "id"]);
            edges = applyEdgeChanges([{ type: "remove", id: text(event.id) }], edges);
            break;
          default: throw new Error("unsupported operation");
        }
      }
      return { nodes: nodes.map(n => ({ id: n.id, position: n.position, selected: n.selected ?? false, dragging: n.dragging ?? false })), edges };
    },
    close() {},
  };
}
