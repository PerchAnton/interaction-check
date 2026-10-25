// Use the client reactive runtime explicitly; Node's default export is the SSR implementation.
import {
  createRoot,
  createSignal,
  createMemo,
  createComputed,
  batch,
} from "solid-js/dist/solid.js";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let selected,
    left,
    right,
    useLeft,
    setters,
    dispose,
    seen = [];
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op", "left", "right"]);
        const l = text(e.left),
          r = text(e.right);
        dispose?.();
        seen = [];
        createRoot((stop) => {
          dispose = stop;
          const [a, setA] = createSignal(l),
            [b, setB] = createSignal(r),
            [pick, setPick] = createSignal(true);
          left = a;
          right = b;
          useLeft = pick;
          setters = { left: setA, right: setB, select: setPick };
          selected = createMemo(() => (useLeft() ? left() : right()));
          createComputed(() => {
            seen.push(selected());
          });
        });
      } else {
        if (!selected) throw new Error("new must be first");
        switch (e.op) {
          case "set":
            fields(e, ["op", "side", "value"]);
            setters[choice(e.side, ["left", "right"])](text(e.value));
            break;
          case "select":
            fields(e, ["op", "side"]);
            setters.select(choice(e.side, ["left", "right"]) === "left");
            break;
          case "batch": {
            fields(e, ["op", "left", "right", "side"]);
            const l = text(e.left),
              r = text(e.right),
              side = choice(e.side, ["left", "right"]);
            batch(() => {
              setters.left(l);
              setters.right(r);
              setters.select(side === "left");
            });
            break;
          }
          case "stop":
            fields(e, ["op"]);
            dispose();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        selected: selected(),
        left: left(),
        right: right(),
        seen: [...seen],
      };
    },
    close() {
      dispose?.();
    },
  };
}
