import * as Y from "yjs";
import { fields, text, index, choice } from "../protocol.mjs";

export function create() {
  let docs, undo;
  const close = () => {
    undo?.forEach((u) => u.destroy());
    docs?.forEach((d) => d.destroy());
  };
  const peer = (value) => (choice(value, ["a", "b"]) === "a" ? 0 : 1);
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op", "text"]);
        close();
        docs = [new Y.Doc(), new Y.Doc()];
        docs[0].getText("body").insert(0, text(event.text));
        Y.applyUpdate(docs[1], Y.encodeStateAsUpdate(docs[0]));
        undo = docs.map(
          (d) =>
            new Y.UndoManager(d.getText("body"), {
              trackedOrigins: new Set(["local"]),
              captureTimeout: 0,
            }),
        );
      } else {
        if (!docs) throw new Error("new must be first");
        switch (event.op) {
          case "insert": {
            fields(event, ["op", "peer", "index", "text"]);
            const p = peer(event.peer),
              body = docs[p].getText("body");
            docs[p].transact(
              () =>
                body.insert(index(event.index, body.length), text(event.text)),
              "local",
            );
            break;
          }
          case "sync": {
            fields(event, ["op", "from", "to"]);
            Y.applyUpdate(
              docs[peer(event.to)],
              Y.encodeStateAsUpdate(docs[peer(event.from)]),
              "remote",
            );
            break;
          }
          case "undo":
          case "redo":
            fields(event, ["op", "peer"]);
            undo[peer(event.peer)][event.op]();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        a: docs[0].getText("body").toString(),
        b: docs[1].getText("body").toString(),
        undo: undo.map((u) => u.undoStack.length),
        redo: undo.map((u) => u.redoStack.length),
      };
    },
    close,
  };
}
