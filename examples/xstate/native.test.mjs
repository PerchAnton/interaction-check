// Ordinary native tests: same example machine and assertions, no JSONL adapter or Python.
import { test } from "node:test";
import { partialDeepStrictEqual as check } from "node:assert/strict";
import { createActor } from "xstate";
import { machine } from "./machine.mjs";

const state = (actor) => {
  const snapshot = actor.getSnapshot();
  return { value: snapshot.value, context: snapshot.context, status: snapshot.status,
    can_save: snapshot.can({ type: "SAVE" }) };
};

test("cancel keeps saved text and the next edit starts from it", (t) => {
  const actor = createActor(machine).start();
  t.after(() => actor.stop());
  check(state(actor), { value: "idle", context: { saved: "original" } });
  actor.send({ type: "EDIT" });
  check(state(actor), { value: "editing" });
  actor.send({ type: "CHANGE", value: "preview" });
  check(state(actor), { context: { draft: "preview", saved: "original" } });
  actor.send({ type: "CANCEL" });
  check(state(actor), { value: "idle", context: { saved: "original" } });
  actor.send({ type: "EDIT" });
  check(state(actor), { context: { draft: "original" } });
});

test("reject blank input, then save a valid correction", (t) => {
  const actor = createActor(machine).start();
  t.after(() => actor.stop());
  check(state(actor), { value: "idle" });
  actor.send({ type: "EDIT" });
  check(state(actor), { value: "editing" });
  actor.send({ type: "CHANGE", value: " " });
  check(state(actor), { can_save: false });
  actor.send({ type: "SAVE" });
  check(state(actor), { value: "editing", context: { saved: "original" } });
  actor.send({ type: "CHANGE", value: "界🙂" });
  check(state(actor), { can_save: true });
  actor.send({ type: "SAVE" });
  check(state(actor), { value: "idle", context: { saved: "界🙂" } });
});

test("restore persisted draft before saving", (t) => {
  let actor = createActor(machine).start();
  t.after(() => actor.stop());
  check(state(actor), { value: "idle" });
  actor.send({ type: "EDIT" });
  check(state(actor), { value: "editing" });
  actor.send({ type: "CHANGE", value: "saved draft" });
  check(state(actor), { context: { draft: "saved draft" } });
  const saved = JSON.parse(JSON.stringify(actor.getPersistedSnapshot()));
  check(state(actor), { value: "editing" });
  actor.send({ type: "CHANGE", value: "later" });
  check(state(actor), { context: { draft: "later" } });
  actor.stop();
  actor = createActor(machine, { snapshot: saved }).start();
  check(state(actor), { value: "editing", context: { draft: "saved draft", saved: "original" } });
  actor.send({ type: "SAVE" });
  check(state(actor), { value: "idle", context: { saved: "saved draft" } });
});
