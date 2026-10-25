import { runSaga, stdChannel } from "redux-saga";
import { take, put, takeLatest, cancelled } from "redux-saga/effects";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let channel,
    task,
    completed = [],
    cancelledIds = [],
    fault;
  const close = () => {
    task?.cancel();
    channel?.close();
  };
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op"]);
        close();
        completed = [];
        cancelledIds = [];
        fault = undefined;
        channel = stdChannel();
        function* worker(action) {
          try {
            const response = yield take(
              (e) => e.type === "resolve" && e.id === action.id,
            );
            yield put({ type: "done", id: action.id, value: response.value });
          } finally {
            if (yield cancelled()) cancelledIds.push(action.id);
          }
        }
        function* root() {
          yield takeLatest("request", worker);
        }
        task = runSaga(
          {
            channel,
            dispatch: (action) =>
              completed.push({ id: action.id, value: action.value }),
            onError: (error) => {
              fault = error;
            },
          },
          root,
        );
      } else {
        if (!task) throw new Error("new must be first");
        switch (e.op) {
          case "request":
            fields(e, ["op", "id"]);
            channel.put({ type: "request", id: choice(e.id, ["a", "b"]) });
            break;
          case "resolve":
            fields(e, ["op", "id", "value"]);
            channel.put({
              type: "resolve",
              id: choice(e.id, ["a", "b"]),
              value: text(e.value),
            });
            break;
          case "stop":
            fields(e, ["op"]);
            task.cancel();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      if (fault) throw fault;
      return {
        completed: [...completed],
        cancelled: [...cancelledIds],
        running: task.isRunning(),
      };
    },
    close,
  };
}
