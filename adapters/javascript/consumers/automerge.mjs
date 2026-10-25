import * as A from "@automerge/automerge";
import { fields, index, text, choice } from "../protocol.mjs";

export function create() {
  let docs, saved;
  const peer = (value) => (choice(value, ["a", "b"]) === "a" ? 0 : 1);
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op", "text"]);
        const first = A.from({ text: text(event.text) }, { actor: "aaaa" });
        docs = [first, A.clone(first, { actor: "bbbb" })];
        saved = undefined;
      } else {
        if (!docs) throw new Error("new must be first");
        switch (event.op) {
          case "insert": {
            fields(event, ["op", "peer", "index", "text"]);
            const p = peer(event.peer),
              at = index(event.index, docs[p].text.length),
              value = text(event.text);
            docs[p] = A.change(docs[p], (d) =>
              A.splice(d, ["text"], at, 0, value),
            );
            break;
          }
          case "merge": {
            fields(event, ["op", "from", "to"]);
            const to = peer(event.to);
            docs[to] = A.merge(docs[to], docs[peer(event.from)]);
            break;
          }
          case "roundtrip": {
            fields(event, ["op", "peer"]);
            const p = peer(event.peer);
            docs[p] = A.load(A.save(docs[p]));
            break;
          }
          case "checkpoint":
            fields(event, ["op"]);
            saved = A.getHeads(docs[0]);
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        a: docs[0].text,
        b: docs[1].text,
        checkpoint: saved ? A.view(docs[0], saved).text : null,
        same_heads:
          JSON.stringify(A.getHeads(docs[0]).sort()) ===
          JSON.stringify(A.getHeads(docs[1]).sort()),
      };
    },
  };
}
