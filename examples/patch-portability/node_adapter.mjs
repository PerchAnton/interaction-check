import { immutableJSONPatch } from 'immutable-json-patch';
import { createInterface } from 'node:readline';
let document = null;
for await (const line of createInterface({ input: process.stdin })) {
  const request = JSON.parse(line);
  if (request.protocol !== 1 || Object.keys(request).sort().join() !== 'event,id,protocol') throw new Error('invalid protocol');
  const event = request.event;
  let error = null;
  if (event.op === 'new') document = structuredClone(event.data);
  else if (event.op === 'apply') {
    try { document = immutableJSONPatch(document, event.patch); }
    catch (exception) {
      if (!(exception instanceof Error)) throw exception;
      error = 'rejected';
    }
  } else throw new Error('unknown event');
  console.log(JSON.stringify({ protocol: 1, id: request.id, state: { document, error } }));
}
