// Real observer output becomes input to the same trace in other runtimes.
import { JSONPatcherProxy } from 'jsonpatcherproxy';
import { writeFileSync } from 'node:fs';
const original = { 'a/b': 1, list: ['a', 'b', 'c'] };
const observer = new JSONPatcherProxy(structuredClone(original));
let batch = [];
const proxy = observer.observe(false, patch => batch.push(structuredClone(patch)));
const steps = [{ event: { op: 'new', data: original }, expect: { document: original, error: null } }];
for (const edit of [() => { proxy['a/b'] = 2; }, () => { proxy.list.splice(1, 1); }]) {
  batch = [];
  edit();
  steps.push({ event: { op: 'apply', patch: batch }, expect: { document: JSON.parse(JSON.stringify(proxy)), error: null } });
}
observer.disableTraps();
writeFileSync(new URL('./scenarios/producer.json', import.meta.url), JSON.stringify({ schema: 1, name: 'observer-to-other-runtimes', steps }, null, 2) + '\n');
