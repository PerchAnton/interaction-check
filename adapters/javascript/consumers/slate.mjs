import { createEditor, Transforms, Node, Editor } from "slate";
import { withHistory, HistoryEditor } from "slate-history";
import { fields, index, text } from "../protocol.mjs";

export function create() {
  let editor;
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op", "text"]);
        editor = withHistory(createEditor());
        editor.children = [
          { type: "paragraph", children: [{ text: text(event.text) }] },
        ];
        Transforms.select(editor, { path: [0, 0], offset: 0 });
      } else {
        if (!editor) throw new Error("new must be first");
        switch (event.op) {
          case "select": {
            fields(event, ["op", "from", "to"]);
            const size = Node.string(editor.children[0]).length;
            Transforms.select(editor, {
              anchor: { path: [0, 0], offset: index(event.from, size) },
              focus: { path: [0, 0], offset: index(event.to, size) },
            });
            break;
          }
          case "insert":
            fields(event, ["op", "text"]);
            HistoryEditor.withNewBatch(editor, () =>
              editor.insertText(text(event.text)),
            );
            break;
          case "delete":
            fields(event, ["op"]);
            HistoryEditor.withNewBatch(editor, () => Transforms.delete(editor));
            break;
          case "undo":
          case "redo":
            fields(event, ["op"]);
            HistoryEditor[event.op](editor);
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      Editor.normalize(editor);
      return {
        text: editor.children.map(Node.string).join("\n"),
        selection: editor.selection,
        undo: editor.history.undos.length,
        redo: editor.history.redos.length,
      };
    },
  };
}
