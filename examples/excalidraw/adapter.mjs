import { JSDOM } from "jsdom";
import { createCanvas } from "@napi-rs/canvas";
import { fields, index } from "../xstate/protocol.mjs";

const dom = new JSDOM("<!doctype html><html><body></body></html>", { url: "http://localhost/" });
globalThis.window = dom.window;
globalThis.document = dom.window.document;
globalThis.devicePixelRatio = 1;
for (const name of ["Element", "HTMLElement", "HTMLCanvasElement", "Node", "CustomEvent"]) globalThis[name] = dom.window[name];
const canvases = new WeakMap();
dom.window.HTMLCanvasElement.prototype.getContext = function (kind) {
  if (!canvases.has(this)) canvases.set(this, createCanvas(this.width, this.height));
  return canvases.get(this).getContext(kind);
};
export const core = (await import("../../.artifacts/excalidraw-core.cjs")).default;
export function fixture() {
  return core.convertToExcalidrawElements([
    { type: "rectangle", id: "a", x: 10, y: 20, width: 30, height: 40 },
  ], { regenerateIds: false });
}
export function create() {
  let elements, saved;
  return {
    step(event) {
      if (event.op === "new") { fields(event, ["op"]); elements = fixture(); saved = undefined; }
      else {
        if (!elements) throw new Error("new must be first");
        switch (event.op) {
          case "move": fields(event, ["op", "x", "y"]); core.mutateElement(elements[0], { x: index(event.x), y: index(event.y) }); break;
          case "delete": fields(event, ["op"]); core.mutateElement(elements[0], { isDeleted: true }); break;
          case "save": fields(event, ["op"]); saved = JSON.stringify(elements); break;
          case "restore":
            fields(event, ["op"]);
            if (!saved) throw new Error("save required");
            elements = core.restoreElements(JSON.parse(saved), null, { repairBindings: true });
            break;
          default: throw new Error("unsupported operation");
        }
      }
      return { elements: elements.map(e => ({ id: e.id, x: e.x, y: e.y, width: e.width, height: e.height, deleted: e.isDeleted, version: e.version })) };
    }, close() { dom.window.close(); },
  };
}
