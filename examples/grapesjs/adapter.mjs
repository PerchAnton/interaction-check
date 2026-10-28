import { JSDOM } from "jsdom";
import { fields, text } from "../xstate/protocol.mjs";
// The real headless editor still requires a document for its model parser.
const dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost/" });
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.DOMParser = dom.window.DOMParser;
const { default: grapesjs } = await import("grapesjs");
export function fixture() {
  const editor = grapesjs.init({ headless: true, storageManager: false });
  const component = editor.addComponents({ tagName: "div", attributes: { id: "a" } })[0];
  editor.UndoManager.clear();
  return { editor, component };
}
export function create() {
  let host;
  return {
    step(event) {
      if (event.op === "new") { fields(event, ["op"]); host?.editor.destroy(); host = fixture(); }
      else {
        if (!host) throw new Error("new must be first");
        switch (event.op) {
          case "rename": fields(event, ["op", "name"]); host.component.set("name", text(event.name)); break;
          // Explicit single stack entries; default true also undoes a same-turn group.
          case "undo": fields(event, ["op"]); host.editor.UndoManager.undo(false); break;
          case "redo": fields(event, ["op"]); host.editor.UndoManager.redo(false); break;
          default: throw new Error("unsupported operation");
        }
      }
      const u = host.editor.UndoManager;
      return { name: host.component.get("name"), undo: u.hasUndo(), redo: u.hasRedo(), stack: u.getStack().length };
    },
    close() { host?.editor.destroy(); dom.window.close(); },
  };
}
