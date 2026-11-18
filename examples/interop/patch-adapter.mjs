import { applyBridge } from './patch-bridge.mjs';
import { fields } from '../xstate/protocol.mjs';
import { apply } from 'mutative';
export function createPatchAdapter({ bridge = true } = {}) {
  let document = {};
  return event => {
    let error = null;
    if (event.op === 'new') {
      fields(event, ['op', 'data']);
      if (!event.data || typeof event.data !== 'object' || Array.isArray(event.data)) throw new Error('object required');
      document = structuredClone(event.data);
    } else if (event.op === 'apply') {
      fields(event, ['op', 'patch']);
      try { document = bridge ? applyBridge(document, event.patch) : apply(document, event.patch); }
      catch { error = 'rejected'; }
    } else throw new Error('unknown operation');
    return { document: structuredClone(document), error };
  };
}
