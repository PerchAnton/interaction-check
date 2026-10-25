import { serve } from "./protocol.mjs";

const consumers = new Set([
  "slate",
  "lexical",
  "tiptap",
  "quill",
  "immer",
  "zustand",
  "xstate",
  "yjs",
  "automerge",
  "redux-toolkit",
]);
const name = process.argv[2];
try {
  if (!consumers.has(name)) throw new Error("choose a documented consumer");
  const { create } = await import(`./consumers/${name}.mjs`);
  const adapter = await create();
  try {
    await serve(adapter.step);
  } finally {
    adapter.close?.();
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = 1;
}
