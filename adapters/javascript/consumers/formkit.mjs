import { createNode, createMessage, reset } from "@formkit/core";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let group, nodes;
  return {
    async step(e) {
      if (e.op === "new") {
        fields(e, ["op", "title", "note"]);
        const title = text(e.title),
          note = text(e.note);
        group?.destroy();
        nodes = {
          title: createNode({ name: "title", value: title }),
          note: createNode({ name: "note", value: note }),
        };
        group = createNode({
          type: "group",
          children: [nodes.title, nodes.note],
        });
        group.ledger.count("blocking", (m) => m.blocking);
      } else {
        if (!group) throw new Error("new must be first");
        switch (e.op) {
          case "input":
            fields(e, ["op", "field", "value"]);
            nodes[choice(e.field, ["title", "note"])].input(
              text(e.value),
              false,
            );
            break;
          case "reset":
            fields(e, ["op"]);
            reset(group);
            break;
          case "error":
            fields(e, ["op", "field", "value"]);
            nodes[choice(e.field, ["title", "note"])].store.set(
              createMessage({
                key: "server",
                type: "error",
                blocking: true,
                value: text(e.value),
              }),
            );
            break;
          case "clear":
            fields(e, ["op", "field"]);
            nodes[choice(e.field, ["title", "note"])].store.remove("server");
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      await group.settled;
      return {
        value: { ...group.value },
        blocking: group.ledger.value("blocking"),
        settled: group.isSettled,
      };
    },
    close() {
      group?.destroy();
    },
  };
}
