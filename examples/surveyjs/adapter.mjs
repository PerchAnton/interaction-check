import { Model } from "survey-core";
import { fields, text, choice } from "../xstate/protocol.mjs";

export const schema = {
  clearInvisibleValues: "onHidden",
  pages: [
    { name: "identity", elements: [{ type: "text", name: "name", isRequired: true }] },
    { name: "details", elements: [
      { type: "boolean", name: "extra" },
      { type: "text", name: "detail", visibleIf: "{extra} = true" },
    ] },
  ],
};

export function create() {
  let survey;
  let result = null;
  let completions = 0;
  return {
    step(event) {
      if (event.op === "new") {
        fields(event, ["op"]);
        survey?.dispose();
        survey = new Model(schema);
        result = null;
        completions = 0;
        survey.onComplete.add(() => completions++);
      } else {
        if (!survey) throw new Error("new must be first");
        switch (event.op) {
          case "set": {
            fields(event, ["op", "name", "value"]);
            const name = choice(event.name, ["name", "detail", "extra"]);
            const value = name === "extra" ? choice(event.value, [true, false]) : text(event.value);
            survey.setValue(name, value);
            result = null;
            break;
          }
          case "next": fields(event, ["op"]); result = survey.nextPage(); break;
          case "back": fields(event, ["op"]); result = survey.prevPage(); break;
          case "complete": fields(event, ["op"]); result = survey.tryComplete(); break;
          case "clear": fields(event, ["op"]); survey.clear(); result = null; break;
          default: throw new Error("unsupported operation");
        }
      }
      return {
        data: survey.data,
        detail_value: survey.getValue("detail") ?? null,
        page: survey.currentPage?.name ?? null,
        visible: survey.getAllQuestions().filter(q => q.isVisible).map(q => q.name),
        errors: survey.getAllQuestions().filter(q => q.errors.length).map(q => q.name),
        completed: survey.isCompleted, completions, result,
      };
    },
    close() { survey?.dispose(); },
  };
}
