import test from "node:test";
import assert from "node:assert/strict";
import { Model } from "survey-core";
import { schema, create } from "./adapter.mjs";

test("required navigation and hidden values use the real SurveyJS model", () => {
  const survey = new Model(schema);
  try {
    assert.equal(survey.nextPage(), false);
    assert.equal(survey.currentPage.name, "identity");
    survey.setValue("name", "Test");
    assert.equal(survey.nextPage(), true);
    survey.setValue("extra", true);
    survey.setValue("detail", "temporary");
    survey.setValue("extra", false);
    assert.equal(survey.getValue("detail"), undefined);
    assert.equal(survey.getQuestionByName("detail").isVisible, false);
  } finally { survey.dispose(); }
});

test("adapter rejects expected state and unknown operations; new resets", () => {
  const adapter = create();
  try {
    assert.throws(() => adapter.step({ op: "next" }));
    assert.throws(() => adapter.step({ op: "new", expect: {} }));
    adapter.step({ op: "new" });
    assert.throws(() => adapter.step({ op: "invented" }));
    adapter.step({ op: "set", name: "name", value: "changed" });
    assert.deepEqual(adapter.step({ op: "new" }).data, {});
  } finally { adapter.close(); }
});
