import { createInterface } from 'node:readline';
import { tinyController } from './events.mjs';
const step = tinyController();
for await (const line of createInterface({ input: process.stdin })) {
  const request = JSON.parse(line);
  if (request.protocol !== 1 || Object.keys(request).sort().join() !== 'event,id,protocol') throw new Error('Invalid protocol');
  console.log(JSON.stringify({ protocol: 1, id: request.id, state: step(request.event) }));
}
