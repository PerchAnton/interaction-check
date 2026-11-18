import mitt from 'mitt';
import { Signal } from 'typed-signals';
import Emittery from 'emittery';
import contra from 'contra';

// Only the application-facing subscribe, unsubscribe and awaited emit boundary.
export function emitter(library) {
  if (library === 'mitt') {
    const bus = mitt();
    return { on: f => bus.on('value', f), off: f => bus.off('value', f), emit: v => bus.emit('value', v) };
  }
  if (library === 'typed-signals') {
    const signal = new Signal();
    return { on: f => signal.connect(f), off: f => signal.disconnect(f), emit: v => signal.emit(v) };
  }
  if (library === 'emittery') {
    const bus = new Emittery();
    const wrappers = new Map();
    return {
      on: f => { const wrapper = ({ data }) => f(data); wrappers.set(f, wrapper); return bus.on('value', wrapper); },
      off: f => { bus.off('value', wrappers.get(f) ?? f); wrappers.delete(f); },
      emit: v => bus.emit('value', v),
    };
  }
  if (library === 'contra') {
    const bus = contra.emitter();
    return { on: f => bus.on('value', f), off: f => bus.off('value', f), emit: v => bus.emit('value', v) };
  }
  throw new Error(`Unknown library: ${library}`);
}

export function controller(library) {
  let bus, handlers, value, writes, emissions, callbacks, log;
  return async event => {
    callbacks = [];
    switch (event.op) {
      case 'new': bus = emitter(library); handlers = new Map(); value = null; writes = 0; emissions = 0; log = []; break;
      case 'write': value = event.value; writes++; break;
      case 'on': {
        if (handlers.has(event.listener)) throw new Error('Duplicate application listener id');
        const f = v => { const row = [event.listener, v]; callbacks.push(row); log.push(row); };
        handlers.set(event.listener, f); bus.on(f); break;
      }
      case 'off': bus.off(handlers.get(event.listener) ?? (() => {})); break;
      case 'emit': emissions++; await bus.emit(value); break;
      default: throw new Error('Unknown event');
    }
    return structuredClone({ value, writes, emissions, callbacks, log });
  };
}
