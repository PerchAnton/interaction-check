import { Rect, Group } from "fabric";
import { fields, choice, index } from "../xstate/protocol.mjs";
export function fixture() {
  const a = new Rect({ left: 10, top: 10, width: 10, height: 10, strokeWidth: 0, originX: "center", originY: "center" });
  const b = new Rect({ left: 30, top: 10, width: 10, height: 10, strokeWidth: 0, originX: "center", originY: "center" });
  return { a, b, group: new Group([a, b]) };
}
const round = value => Math.round(value * 1e6) / 1e6;
export function create() {
  let host;
  return {
    step(event) {
      if (event.op === "new") { fields(event, ["op"]); host?.group.dispose(); host = fixture(); }
      else {
        if (!host) throw new Error("new must be first");
        switch (event.op) {
          case "move":
            fields(event, ["op", "dx", "dy"]);
            host.group.set({ left: host.group.left + index(event.dx), top: host.group.top + index(event.dy) });
            host.group.setCoords();
            break;
          case "remove": fields(event, ["op", "id"]); host.group.remove(host[choice(event.id, ["a", "b"])]); break;
          case "add": fields(event, ["op", "id"]); host.group.add(host[choice(event.id, ["a", "b"])]); break;
          default: throw new Error("unsupported operation");
        }
      }
      return { members: ["a", "b"].filter(id => host.group.contains(host[id])), objects: ["a", "b"].map(id => {
        const point = host[id].getCenterPoint();
        return { id, x: round(point.x), y: round(point.y) };
      }) };
    }, close() { host?.group.dispose(); },
  };
}
