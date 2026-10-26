import { createSelector, lruMemoize } from "reselect";
import { fields, text, index, choice } from "../protocol.mjs";
export function create() {
  let state, selector, previous;
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op"]);
        state = { items: [], theme: "light" };
        previous = undefined;
        selector = createSelector(
          [(s) => s.items],
          (items) => items.filter((x) => x.done).map((x) => x.title),
          {
            memoize: lruMemoize,
            memoizeOptions: {
              resultEqualityCheck: (a, b) =>
                a.length === b.length && a.every((x, i) => x === b[i]),
            },
          },
        );
      } else {
        if (!state) throw new Error("new must be first");
        switch (e.op) {
          case "append":
            fields(e, ["op", "title", "done"]);
            state = {
              ...state,
              items: [
                ...state.items,
                { title: text(e.title), done: choice(e.done, [true, false]) },
              ],
            };
            break;
          case "toggle":
            fields(e, ["op", "at"]);
            {
              const at = index(e.at, state.items.length - 1);
              state = {
                ...state,
                items: state.items.map((x, i) =>
                  i === at ? { ...x, done: !x.done } : x,
                ),
              };
            }
            break;
          case "theme":
            fields(e, ["op", "value"]);
            state = { ...state, theme: text(e.value) };
            break;
          case "same":
            fields(e, ["op"]);
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      const titles = selector(state),
        same = titles === previous;
      previous = titles;
      return {
        titles: [...titles],
        recomputations: selector.recomputations(),
        same,
      };
    },
  };
}
