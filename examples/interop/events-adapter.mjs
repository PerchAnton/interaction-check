import EventEmitter2 from 'eventemitter2';
import { fields } from '../xstate/protocol.mjs';

export function createEventsAdapter({ normalized = true } = {}) {
  let emitter;
  let log = [];
  let value = null;
  let writes = 0;
  let emissions = 0;
  const listeners = new Set();
  return event => {
    const before = log.length;
    if (event.op === 'new') {
      fields(event, ['op']); emitter?.removeAllListeners();
      emitter = new EventEmitter2({ wildcard: true, newListener: false });
      log = []; value = null; writes = 0; emissions = 0; listeners.clear();
    } else {
      if (!emitter) throw new Error('new must be first');
      if (event.op === 'on') {
        fields(event, ['op', 'listener', 'name']);
        if (typeof event.listener !== 'string' || listeners.has(event.listener) || listeners.size >= 16
          || typeof event.name !== 'string') throw new Error('unique listener and string name required');
        listeners.add(event.listener);
        emitter.on(event.name, payload => log.push({ listener: event.listener, value: payload ?? null }));
      } else if (event.op === 'write') {
        fields(event, ['op', 'value']); value = structuredClone(event.value); writes++;
      } else if (event.op === 'emit') {
        fields(event, ['op', 'name']);
        if (!(typeof event.name === 'string' || (Array.isArray(event.name) && event.name.length > 0
          && event.name.length <= 8 && event.name.every(part => typeof part === 'string')))) throw new Error('invalid name');
        let name = event.name;
        // A narrow consumer workaround for #316, not a new interpretation of all array namespaces.
        if (normalized && Array.isArray(name) && name.length === 1 && name[0] === 'newListener') name = 'newListener';
        emitter.emit(name, structuredClone(value)); emissions++;
      } else throw new Error('unknown operation');
    }
    return { value: structuredClone(value), writes, emissions,
      callbacks: structuredClone(log.slice(event.op === 'new' ? 0 : before)), log: structuredClone(log) };
  };
}
