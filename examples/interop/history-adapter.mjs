import { createStore } from 'zustand/vanilla';
import { temporal } from 'zundo';
import { fields } from '../xstate/protocol.mjs';

export function createHistoryAdapter({ guarded = true } = {}) {
  let store;
  let log = [];
  let stop = () => {};
  const value = state => state === undefined ? { missing: true, value: null } : { missing: false, value: state.value };
  return event => {
    const before = log.length;
    if (event.op === 'new') {
      fields(event, ['op']); stop(); log = [];
      store = createStore(temporal(() => ({ value: 0 })));
      stop = store.subscribe(state => log.push(value(state)));
    } else {
      if (!store) throw new Error('new must be first');
      if (event.op === 'set') {
        fields(event, ['op', 'value']);
        if (!Number.isSafeInteger(event.value)) throw new Error('safe integer required');
        store.setState({ value: event.value });
      } else if (event.op === 'undo' || event.op === 'redo') {
        fields(event, ['op'], ['steps']);
        const steps = Object.hasOwn(event, 'steps') ? event.steps : 1;
        // Explicit application policy: invalid counts are no-ops. Upstream may choose a different policy.
        if (!guarded || (Number.isSafeInteger(steps) && steps > 0)) store.temporal.getState()[event.op](steps);
      } else throw new Error('unknown operation');
    }
    const history = store.temporal.getState();
    return { ...value(store.getState()), past: history.pastStates.map(value), future: history.futureStates.map(value),
      callbacks: structuredClone(log.slice(event.op === 'new' ? 0 : before)), log: structuredClone(log) };
  };
}
