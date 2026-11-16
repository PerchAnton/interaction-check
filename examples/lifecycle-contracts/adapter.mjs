import { createInterface } from 'node:readline';
import { controller } from './emitter.mjs';
const step = controller(process.argv[2]);
for await (const line of createInterface({ input: process.stdin })) {
  const request = JSON.parse(line);
  if (request.protocol !== 1 || Object.keys(request).sort().join() !== 'event,id,protocol') throw new Error('Invalid protocol');
  console.log(JSON.stringify({ protocol: 1, id: request.id, state: await step(request.event) }));
}
