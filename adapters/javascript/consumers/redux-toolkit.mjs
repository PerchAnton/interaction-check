import {
  configureStore,
  createEntityAdapter,
  createSlice,
} from "@reduxjs/toolkit";
import { fields, text } from "../protocol.mjs";

export function create() {
  const entities = createEntityAdapter({
    sortComparer: (a, b) =>
      a.title < b.title ? -1 : a.title > b.title ? 1 : 0,
  });
  const slice = createSlice({
    name: "documents",
    initialState: entities.getInitialState(),
    reducers: {
      add: entities.addOne,
      update: entities.updateOne,
      remove: entities.removeOne,
    },
  });
  let store, original;
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op"]);
        store = configureStore({ reducer: slice.reducer });
        original = store.getState();
      } else {
        if (!store) throw new Error("new must be first");
        switch (event.op) {
          case "add":
            fields(event, ["op", "id", "title"]);
            store.dispatch(
              slice.actions.add({
                id: text(event.id),
                title: text(event.title),
              }),
            );
            break;
          case "update":
            fields(event, ["op", "id", "title"]);
            store.dispatch(
              slice.actions.update({
                id: text(event.id),
                changes: { title: text(event.title) },
              }),
            );
            break;
          case "remove":
            fields(event, ["op", "id"]);
            store.dispatch(slice.actions.remove(text(event.id)));
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return { value: store.getState(), original };
    },
  };
}
