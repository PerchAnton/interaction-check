# Patch portability at an application boundary

These examples replay the same JSON events against installed Python, JavaScript,
Go and Rust packages. The added value is one checked contract for a producer and
several consumers. For one implementation, the small native tests here are the
simpler choice. No upstream project needs to adopt a Python runner for them.

## What actually runs

| Package | Boundary exercised |
| --- | --- |
| python-jsonpath 2.2.2 | JSON Patch, with Unicode-escape extension disabled |
| jsonpatch 1.47 | In-place JSON Patch on an unpublished copy |
| immutable-json-patch 6.0.3 | Immutable patch application and a native inverse test |
| JSONPatcherProxy 0.1.0-0 | Real callback patches exported to the other consumers |
| evanphx/json-patch v5.9.11 | Go application, negative-index extension disabled |
| idubrov/json-patch 5.0.0 | Rust atomic patch and merge patch |
| json-merge-patch 0.3.0 | RFC 7396 null/removal, array replacement and idempotence |
| wI2L/jsondiff 0.7.1 | Native diff/apply round trip, including a known failing case |

The Python adapters copy before applying and publish only on success. That is
application policy, not a claim that native in-place APIs roll back. A native
test shows the difference. Rust's native `patch` already rolls back a rejected
batch; an extra copy is unnecessary there. Merge patch is a separate contract,
not JSON Patch under another name. These examples are not a full RFC suite.

`producer.mjs` edits a real proxy and exports its callback batches. The expected
document comes from the edited object, not another patch implementation. The
trace is consumed by Python, JavaScript, Go and Rust. Writes, callbacks, the
cumulative callback log and consumer state remain distinct in `native.test.mjs`.

## Run

From the repository root, use Python 3.14, Node 24, Go 1.27.4 and Rust 1.99.1:

```sh
python -m venv .venv-patch
. .venv-patch/bin/activate
python -m pip install -r examples/patch-portability/requirements.txt
npm --prefix examples/patch-portability ci --ignore-scripts
python examples/patch-portability/native_test.py
node --test examples/patch-portability/native.test.mjs
node examples/patch-portability/producer.mjs
cargo test --locked --manifest-path examples/patch-portability/rust/Cargo.toml
cargo build --locked --manifest-path examples/patch-portability/rust/Cargo.toml
mkdir -p artifacts
go -C examples/patch-portability build -o ../../artifacts/patch-go .
python examples/patch-portability/verify.py --output artifacts/patch-portability/reports --go-adapter artifacts/patch-go --rust-adapter examples/patch-portability/rust/target/debug/patch-portability-adapter
```

## Known upstream differences, kept visible

Published python-jsonpath 2.2.2 accepts `true` as equal to `1` in a `test`.
`boolean-is-not-number.json` fails at **step 2, `state.error`**. The adapter's
returned state is preserved in the failed report. [PR #139 already fixed this
upstream](https://github.com/jg-rp/python-jsonpath/pull/139); we do not duplicate
that change. CI also installs source `bd91a15094796927cd683c628169c1a8e8b6ddb6`
in a separate directory and runs the same traces. Its metadata still says 2.2.2;
the source commit, rather than that version string, identifies the comparison.

`go test -v` deliberately fails on published jsondiff 0.7.1: `Rationalize` panics
for a target string ending with a backslash. [Open PR #56](https://github.com/wI2L/jsondiff/pull/56)
contains the fix. `check_fixes.py` retains the published failure log, requires
that specific panic and checks the identical native tests against the supplied
fixed source. CI downloads exact commit `93a94633a7ee0afa1434c29c4e86f1f1b00fb589`.
This is a before/after check, not a passing result for the published library.

With both fixed-source comparisons, local verification retained **32 replay
reports: 31 passed and the expected published python-jsonpath mismatch failed**.
The jsondiff panic is a separate native check. Python native tests (3), Node
native tests (2), Rust atomicity (1), and the fixed Go tests (2) passed. The CI
artifact contains raw reports, hashes and native before/after logs; the script
checks the known discrepancy instead of treating any failure as acceptable.

This small corpus does not measure performance, prove production compatibility,
or replace each library's own suite. Pinning and maintaining adapters is a cost;
use it when the same application data really crosses these runtimes.

### Native inverse comparison

`inverse_probe.mjs` separately checks immutable-json-patch
[PR #8](https://github.com/josdejong/immutable-json-patch/pull/8). On published
6.0.3, the root-array and nested-array moves to `/-` do not round trip; moving
between different arrays does. The returned array contains an actual
`undefined` element, which becomes `null` when JSON is serialized. Both facts
are recorded instead of silently treating that serialization as valid data.

The same three cases pass after building ESM from exact upstream PR head
`d3b9ab0aef94ffb10c78fa0713a0e87bab14696d`. CI keeps both JSON records. The fix
belongs to that upstream PR; it is not a new fix in interaction-check.

```sh
node examples/patch-portability/inverse_probe.mjs
node examples/patch-portability/inverse_probe.mjs --module /path/to/fixed/lib/esm/index.js --fixed
```

The default command asserts the two known failures of the pinned baseline;
`--fixed` requires all three round trips. These are three small native cases,
not an upstream full-suite or performance result.
