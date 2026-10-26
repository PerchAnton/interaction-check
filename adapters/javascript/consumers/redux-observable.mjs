import { legacy_createStore, applyMiddleware } from "redux";
import { createEpicMiddleware, ofType } from "redux-observable";
import { Subject, switchMap, map, takeUntil } from "rxjs";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let store, channels, stop;
  const close = () => {
    stop?.next();
    stop?.complete();
    if (channels)
      Object.values(channels).forEach((channel) => channel.complete());
  };
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op"]);
        close();
        channels = { a: new Subject(), b: new Subject() };
        stop = new Subject();
        const middleware = createEpicMiddleware();
        store = legacy_createStore(
          (s = [], a) =>
            a.type === "done" ? [...s, { id: a.id, value: a.value }] : s,
          applyMiddleware(middleware),
        );
        middleware.run((action$) =>
          action$.pipe(
            ofType("request"),
            switchMap((action) =>
              channels[action.id].pipe(
                map((value) => ({ type: "done", id: action.id, value })),
                takeUntil(action$.pipe(ofType("cancel"))),
              ),
            ),
            takeUntil(stop),
          ),
        );
      } else {
        if (!store) throw new Error("new must be first");
        switch (e.op) {
          case "request":
            fields(e, ["op", "id"]);
            store.dispatch({ type: "request", id: choice(e.id, ["a", "b"]) });
            break;
          case "emit":
            fields(e, ["op", "id", "value"]);
            channels[choice(e.id, ["a", "b"])].next(text(e.value));
            break;
          case "cancel":
            fields(e, ["op"]);
            store.dispatch({ type: "cancel" });
            break;
          case "stop":
            fields(e, ["op"]);
            stop.next();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return { completed: [...store.getState()] };
    },
    close,
  };
}
