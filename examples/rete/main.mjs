import { serve } from "../xstate/protocol.mjs";
import { create } from "./adapter.mjs";
const adapter = create();
try { await serve(adapter.step); }
catch (error) { console.error(error.message); process.exitCode = 1; }
finally { adapter.close(); }
