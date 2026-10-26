import { build } from "esbuild";
import { fileURLToPath } from "node:url";
await build({
  entryPoints: [fileURLToPath(new URL("./library.mjs", import.meta.url))],
  outfile: fileURLToPath(new URL("../../.artifacts/excalidraw-core.cjs", import.meta.url)),
  bundle: true, platform: "node", format: "cjs", target: "node24",
  define: { "process.env.NODE_ENV": '"production"' },
});
