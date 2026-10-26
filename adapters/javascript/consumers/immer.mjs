import { enablePatches, produceWithPatches, applyPatches } from "immer";
import { fields, index, text, choice } from "../protocol.mjs";
enablePatches();

export function create() {
  let state,
    original,
    patches = [],
    inverse = [];
  return {
    step(event) {
      let previous = state;
      if (event.op === "new") {
        fields(event, ["op", "title"]);
        state = {
          title: text(event.title),
          tags: ["one", "two"],
          nested: { enabled: true },
        };
        original = state;
        patches = [];
        inverse = [];
        previous = state;
      } else {
        if (!state) throw new Error("new must be first");
        switch (event.op) {
          case "title":
            fields(event, ["op", "value"]);
            [state, patches, inverse] = produceWithPatches(state, (d) => {
              d.title = text(event.value);
            });
            break;
          case "tag":
            fields(event, ["op", "index", "value"]);
            [state, patches, inverse] = produceWithPatches(state, (d) => {
              d.tags[index(event.index, d.tags.length - 1)] = text(event.value);
            });
            break;
          case "removeTag":
            fields(event, ["op", "index"]);
            [state, patches, inverse] = produceWithPatches(state, (d) => {
              d.tags.splice(index(event.index, d.tags.length - 1), 1);
            });
            break;
          case "apply":
            fields(event, ["op", "direction"]);
            state = applyPatches(
              state,
              choice(event.direction, ["forward", "inverse"]) === "inverse"
                ? inverse
                : patches,
            );
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        value: state,
        original,
        same: state === previous,
        nested_shared: state.nested === original.nested,
        patches,
        inverse,
      };
    },
  };
}
