import TinyEmitter from 'tiny-emitter';
import PubSub from 'pubsub-js';
import { createRequire } from 'node:module';

export function tinyController() {
  const emitter = new TinyEmitter();
  let callbacks = [];
  const log = [], handlers = new Map();
  function handler(name) {
    if (!handlers.has(name)) handlers.set(name, value => { callbacks.push([name, value]); log.push([name, value]); });
    return handlers.get(name);
  }
  return event => {
    callbacks = [];
    if (event.op === 'on') emitter.on('value', handler(event.name));
    else if (event.op === 'once') emitter.once('value', handler(event.name));
    else if (event.op === 'off') emitter.off('value', handler(event.name));
    else if (event.op === 'emit') emitter.emit('value', event.value);
    else if (event.op !== 'snapshot') throw new Error('Unknown operation');
    return { callbacks, log: [...log] };
  };
}

export function topicProbe(method = 'clearSubscriptions', parent = true, modulePath) {
  const pubsub = modulePath ? createRequire(import.meta.url)(modulePath) : PubSub;
  pubsub.clearAllSubscriptions();
  const calls = [];
  try {
    if (parent) pubsub.subscribe('enter', (topic, value) => calls.push([topic, value]));
    pubsub.subscribe('enter.child', (topic, value) => calls.push([topic, value]));
    pubsub.subscribe('entering', (topic, value) => calls.push([topic, value]));
    pubsub[method]('enter');
    for (const topic of ['enter', 'enter.child', 'entering']) pubsub.publishSync(topic, 7);
    return { method, parent, callbacks: calls };
  } finally { pubsub.clearAllSubscriptions(); }
}
