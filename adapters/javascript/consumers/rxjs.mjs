import { Subject, switchMap, distinctUntilChanged, takeUntil } from "rxjs";
import { fields, text, choice } from "../protocol.mjs";
export function create() {
  let requests,
    channels,
    cancel,
    sub,
    values = [],
    completed = false;
  const close = () => {
    sub?.unsubscribe();
    requests?.complete();
    cancel?.complete();
    if (channels)
      Object.values(channels).forEach((channel) => channel.complete());
  };
  return {
    step(e) {
      if (e.op === "new") {
        fields(e, ["op"]);
        close();
        values = [];
        completed = false;
        requests = new Subject();
        channels = { a: new Subject(), b: new Subject() };
        cancel = new Subject();
        sub = requests
          .pipe(
            switchMap((id) => channels[id]),
            distinctUntilChanged(),
            takeUntil(cancel),
          )
          .subscribe({
            next: (value) => values.push(value),
            complete: () => {
              completed = true;
            },
          });
      } else {
        if (!sub) throw new Error("new must be first");
        switch (e.op) {
          case "select":
            fields(e, ["op", "channel"]);
            requests.next(choice(e.channel, ["a", "b"]));
            break;
          case "emit":
            fields(e, ["op", "channel", "value"]);
            channels[choice(e.channel, ["a", "b"])].next(text(e.value));
            break;
          case "cancel":
            fields(e, ["op"]);
            cancel.next();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return { values: [...values], completed, closed: sub.closed };
    },
    close,
  };
}
