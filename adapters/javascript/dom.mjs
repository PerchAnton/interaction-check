import { JSDOM } from "jsdom";

export function installDOM() {
  const dom = new JSDOM(
    '<!doctype html><html><body><div id="editor"></div></body></html>',
  );
  for (const key of [
    "window",
    "document",
    "navigator",
    "Node",
    "Text",
    "Element",
    "HTMLElement",
    "DOMParser",
    "MutationObserver",
    "getComputedStyle",
  ]) {
    Object.defineProperty(globalThis, key, {
      value: dom.window[key],
      configurable: true,
    });
  }
  return dom;
}
