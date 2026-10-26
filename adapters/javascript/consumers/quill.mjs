import { installDOM } from "../dom.mjs";
import { fields, text, index } from "../protocol.mjs";

export async function create() {
  const dom = installDOM();
  const { default: Quill } = await import("quill");
  let editor;
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op", "text"]);
        if (editor) throw new Error("one editor per scenario");
        editor = new Quill(dom.window.document.getElementById("editor"), {
          modules: { toolbar: false, history: { delay: 0 } },
        });
        // jsdom has no layout; scrolling is outside this content/history adapter.
        editor.scrollSelectionIntoView = () => {};
        editor.setText(text(event.text));
        editor.history.clear();
      } else {
        if (!editor) throw new Error("new must be first");
        switch (event.op) {
          case "insert":
            fields(event, ["op", "index", "text"]);
            editor.insertText(
              index(event.index, editor.getLength() - 1),
              text(event.text),
              "user",
            );
            break;
          case "delete":
            fields(event, ["op", "index", "length"]);
            {
              const at = index(event.index, editor.getLength() - 1);
              editor.deleteText(
                at,
                index(event.length, editor.getLength() - at - 1),
                "user",
              );
              break;
            }
          case "bold":
            fields(event, ["op", "index", "length"]);
            {
              const at = index(event.index, editor.getLength() - 1);
              editor.formatText(
                at,
                index(event.length, editor.getLength() - at - 1),
                "bold",
                true,
                "user",
              );
              break;
            }
          case "undo":
          case "redo":
            fields(event, ["op"]);
            editor.history[event.op]();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        text: editor.getText(),
        ops: editor.getContents().ops,
        undo: editor.history.stack.undo.length,
        redo: editor.history.stack.redo.length,
      };
    },
    close() {
      dom.window.close();
    },
  };
}
