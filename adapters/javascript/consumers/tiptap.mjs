import { installDOM } from "../dom.mjs";
import { fields, text, index } from "../protocol.mjs";

export async function create() {
  const dom = installDOM();
  const { Editor } = await import("@tiptap/core");
  const { StarterKit } = await import("@tiptap/starter-kit");
  const { closeHistory } = await import("@tiptap/pm/history");
  let editor;
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op", "text"]);
        editor?.destroy();
        const value = text(event.text);
        editor = new Editor({
          element: dom.window.document.getElementById("editor"),
          extensions: [StarterKit],
          content: {
            type: "doc",
            content: [
              {
                type: "paragraph",
                content: value ? [{ type: "text", text: value }] : [],
              },
            ],
          },
        });
      } else {
        if (!editor) throw new Error("new must be first");
        switch (event.op) {
          case "select":
            fields(event, ["op", "from", "to"]);
            editor.commands.setTextSelection({
              from: index(event.from, editor.state.doc.content.size),
              to: index(event.to, editor.state.doc.content.size),
            });
            break;
          case "insert":
            fields(event, ["op", "text"]);
            editor.view.dispatch(closeHistory(editor.state.tr));
            editor.commands.insertContent({
              type: "text",
              text: text(event.text),
            });
            break;
          case "bold":
            fields(event, ["op"]);
            editor.view.dispatch(closeHistory(editor.state.tr));
            editor.commands.toggleBold();
            break;
          case "undo":
          case "redo":
            fields(event, ["op"]);
            editor.commands[event.op]();
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      return {
        text: editor.getText(),
        json: editor.getJSON(),
        from: editor.state.selection.from,
        to: editor.state.selection.to,
        can_undo: editor.can().undo(),
        can_redo: editor.can().redo(),
      };
    },
    close() {
      editor?.destroy();
      dom.window.close();
    },
  };
}
