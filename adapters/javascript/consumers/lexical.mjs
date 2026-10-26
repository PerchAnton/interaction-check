import { createHeadlessEditor } from "@lexical/headless";
import { registerHistory, createEmptyHistoryState } from "@lexical/history";
import {
  $getRoot,
  $createParagraphNode,
  $createTextNode,
  $getSelection,
  HISTORY_PUSH_TAG,
  UNDO_COMMAND,
  REDO_COMMAND,
} from "lexical";
import { fields, text, index } from "../protocol.mjs";

export function create() {
  let editor, history, unregister, saved;
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op", "text"]);
        unregister?.();
        saved = undefined;
        editor = createHeadlessEditor({
          namespace: "interaction-check",
          onError(error) {
            throw error;
          },
        });
        editor.update(
          () =>
            $getRoot().append(
              $createParagraphNode().append($createTextNode(text(event.text))),
            ),
          { discrete: true },
        );
        history = createEmptyHistoryState();
        unregister = registerHistory(editor, history, 0);
      } else {
        if (!editor) throw new Error("new must be first");
        switch (event.op) {
          case "select":
            fields(event, ["op", "from", "to"]);
            editor.update(
              () => {
                const node = $getRoot().getFirstDescendant(),
                  size = node.getTextContentSize();
                node.select(index(event.from, size), index(event.to, size));
              },
              { discrete: true },
            );
            break;
          case "insert":
            fields(event, ["op", "text"]);
            editor.update(
              () => {
                const selection = $getSelection();
                if (!selection) throw new Error("select before insert");
                selection.insertText(text(event.text));
              },
              { discrete: true, tag: HISTORY_PUSH_TAG },
            );
            break;
          case "undo":
          case "redo":
            fields(event, ["op"]);
            editor.dispatchCommand(
              event.op === "undo" ? UNDO_COMMAND : REDO_COMMAND,
              undefined,
            );
            break;
          case "checkpoint":
            fields(event, ["op"]);
            saved = editor.getEditorState();
            break;
          case "roundtrip":
            fields(event, ["op"]);
            editor.setEditorState(
              editor.parseEditorState(
                JSON.stringify(editor.getEditorState().toJSON()),
              ),
            );
            break;
          default:
            throw new Error("unsupported operation");
        }
      }
      const value = editor.read(() => $getRoot().getTextContent());
      const checkpoint = saved
        ? saved.read(() => $getRoot().getTextContent())
        : null;
      return {
        text: value,
        checkpoint,
        undo: history.undoStack.length,
        redo: history.redoStack.length,
      };
    },
    close() {
      unregister?.();
    },
  };
}
