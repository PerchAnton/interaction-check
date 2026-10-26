import cytoscape from "cytoscape";
import { fields, text } from "../xstate/protocol.mjs";

export function create() {
  let cy;
  let removed;
  const events = { add: 0, remove: 0, select: 0 };
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op"]);
        cy?.destroy();
        cy = cytoscape({ headless: true, elements: [
          { data: { id: "a" } }, { data: { id: "b" } },
          { data: { id: "ab", source: "a", target: "b" } },
        ] });
        removed = undefined;
        for (const name of Object.keys(events)) events[name] = 0;
        cy.on("add remove select", e => events[e.type]++);
      } else {
        if (!cy) throw new Error("new must be first");
        switch (event.op) {
          case "select":
            fields(event, ["op", "id"]);
            cy.getElementById(text(event.id)).select();
            break;
          case "remove":
            fields(event, ["op", "id"]);
            removed = cy.getElementById(text(event.id)).remove();
            break;
          case "remove_again":
            fields(event, ["op"]);
            if (!removed) throw new Error("remove required");
            removed.remove();
            break;
          case "restore":
            fields(event, ["op"]);
            if (!removed) throw new Error("remove required");
            removed.restore();
            break;
          case "reverse_edge":
            fields(event, ["op"]);
            cy.getElementById("ab").move({ source: "b", target: "a" });
            break;
          default: throw new Error("unsupported operation");
        }
      }
      return {
        nodes: cy.nodes().map(e => e.id()).sort(),
        edges: cy.edges().map(e => ({ id: e.id(), source: e.source().id(), target: e.target().id() })),
        selected: cy.$(":selected").map(e => e.id()).sort(),
        events: { ...events },
      };
    },
    close() { cy?.destroy(); },
  };
}
