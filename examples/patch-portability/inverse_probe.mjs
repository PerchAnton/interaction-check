// Native consumer probe for immutable-json-patch #8; no runner dependency.
import assert from 'node:assert/strict';
import { isDeepStrictEqual, parseArgs } from 'node:util';
import { pathToFileURL } from 'node:url';
import { resolve } from 'node:path';
const { values } = parseArgs({ options: { module: { type: 'string' }, fixed: { type: 'boolean', default: false } } });
const library = await import(values.module ? pathToFileURL(resolve(values.module)).href : 'immutable-json-patch');
const cases = [
  { name: 'root array', document: [1, 2, 3], patch: [{ op: 'move', from: '/0', path: '/-' }], affected: true },
  { name: 'nested array', document: { list: ['a', 'b', 'c'] }, patch: [{ op: 'move', from: '/list/0', path: '/list/-' }], affected: true },
  { name: 'different arrays', document: { a: [1, 2], b: [3] }, patch: [{ op: 'move', from: '/a/0', path: '/b/-' }], affected: false },
];
const results = cases.map(({ name, document, patch, affected }) => {
  const original = structuredClone(document);
  const forward = library.immutableJSONPatch(document, patch);
  const inverse = library.revertJSONPatch(document, patch);
  const restored = library.immutableJSONPatch(forward, inverse);
  const roundTrip = isDeepStrictEqual(restored, original);
  assert.deepEqual(document, original, 'input must stay unchanged');
  assert.equal(roundTrip, values.fixed || !affected, `${name}: unexpected result`);
  return { name, document, patch, inverse, roundTrip,
    restoredJSON: JSON.stringify(restored),
    undefinedInRestoredArray: (Array.isArray(restored) ? restored : restored.list ?? []).includes(undefined) };
});
console.log(JSON.stringify({ scope: 'Native round trip, not the upstream full suite', fixedSource: values.fixed, results }, null, 2));
