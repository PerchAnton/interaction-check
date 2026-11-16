# Observable lifecycle contracts

A write, an emission, the callbacks from that emission, and the cumulative log
are separate observations. These adapters use installed packages: mitt 3.0.1,
typed-signals 3.0.0, Emittery 2.2.0 and Contra 1.9.4. They await Emittery and
unwrap its documented `{name, data}` event. They do not force synchronous timing
or identical subscription semantics across these libraries.

```sh
npm --prefix examples/lifecycle-contracts ci --ignore-scripts
node --test examples/lifecycle-contracts/native.test.mjs
python -m pip install interaction-check==1.0.0
python examples/lifecycle-contracts/verify.py --output artifacts/lifecycle
python examples/lifecycle-contracts/check_patch_probes.py --output artifacts/patch-probes
```

The lifecycle check keeps **eight raw reports: seven pass and one fails**.
Contra removes the last registered callback when `off` receives an unknown
callback. `unknown-unsubscribe.json` finds the first mismatch at step 5,
`state.callbacks`: expected `[["a", 7]]`, observed `[]`. The native test keeps
this published discrepancy explicit. It does not call Contra a passing contract.

`native.test.mjs` also pins typed-signals' v3 ordering API: `connect(callback,
{order: 1})`, rather than passing a number as the second argument.

A native test is sufficient for a single emitter. The optional runner is useful
when an application keeps the same JSON contract while comparing implementations
or language boundaries. These two small traces do not prove timing, UI rendering,
performance, all event semantics, or a need to add Python to an upstream project.

## Existing patch fixes: independent native checks

`patch_probe.mjs` imports real published implementations. The checker verifies
specific baseline discrepancies; an unrelated error does not count as success.

| Upstream change | Published observation | Exact-source comparison |
| --- | --- | --- |
| [rfc6902 #114](https://github.com/chbrown/rfc6902/pull/114) | 5.4.0 accepts nine invalid `replace/copy/move` index cases and changes the document | `d60e90f` rejects all nine and preserves the document |
| [jsondiffpatch #444](https://github.com/benjamine/jsondiffpatch/pull/444) | 0.7.7 enables text diffs on existing and fresh plain instances after another instance uses text diffs | `5b1961e` preserves both plain JSON Patch results |
| [fast-json-patch #341](https://github.com/Starcounter-Jack/JSON-Patch/pull/341) | 3.1.1 CommonJS silently ignores child adds to `0`, `false`, and `""`; `null` throws a raw TypeError | `59e4f7a` returns a structured path error for all four; root replacement still works |

For arrays, the rfc6902 probe uses deep equality and records own keys. Comparing
only JSON text would hide a property such as `array['-1']`.

The fixed comparisons used the complete runtime sources at those commits,
transpiled with TypeScript 5.9.3 on Node 24.22.1. They are bounded independent
checks, not a run of the upstream suites or new fixes authored here. To repeat
against built source directories, pass `--rfc6902 PATH`, `--jsondiffpatch PATH`
(the package directory), and `--fast-json-patch PATH` to the checker. Source
revisions must be recorded by the caller; package metadata alone is insufficient.
