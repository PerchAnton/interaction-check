import { serve } from '../xstate/protocol.mjs';
import { createPatchAdapter } from './patch-adapter.mjs';
import { createHistoryAdapter } from './history-adapter.mjs';
import { createEventsAdapter } from './events-adapter.mjs';
const adapters = { patch: () => createPatchAdapter(), 'patch-raw': () => createPatchAdapter({ bridge: false }),
  history: () => createHistoryAdapter(), 'history-raw': () => createHistoryAdapter({ guarded: false }),
  events: () => createEventsAdapter(), 'events-raw': () => createEventsAdapter({ normalized: false }) };
if (!Object.hasOwn(adapters, process.argv[2])) throw new Error('choose patch, history or events (optional -raw)');
try { await serve(adapters[process.argv[2]]()); }
catch (error) { console.error(error.message); process.exitCode = 2; }
