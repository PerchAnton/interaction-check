import { serve } from "../xstate/protocol.mjs";
import { create } from "./adapter.mjs";
const adapter = create();
try { await serve(event => adapter.step(event)); } finally { await adapter.close(); }
