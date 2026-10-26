# Optional Python library adapters

Twenty external examples call the actual published libraries through the bounded
JSONL protocol. The runner remains standard-library-only; these dependencies are
installed only when running these adapters. This is an external reproduction
collection, not an accepted integration into any upstream repository.

Use Python **3.12** for this pinned collection (Pyee 16 requires 3.12+). From the
repository root:

```sh
python -m venv .venv
# Activate .venv using your platform's normal activation command.
python -m pip install -r adapters/python-libraries/requirements.txt
python adapters/python-libraries/replay.py
python -m unittest discover -s adapters/python-libraries/tests -v
```

One consumer, for example:

```sh
python interaction_check.py scenarios/jsonpatch/*.json -- python adapters/python-libraries/main.py jsonpatch
```

`replay.py` expands filenames without shell globs, so the full command also works
on Windows. Each scenario starts a fresh adapter process. Expectations stay in
the runner; adapters receive only events and return observed native state.

## Coverage

**60 hand-authored scenarios / 222 steps**, plus seven adapter boundary tests.
Versions of direct and transitive dependencies are pinned in `requirements.txt`;
`requirements.in` lists the twenty direct consumers. Full native upstream test
suites are not part of these examples. CI replays this collection on Python 3.12
under Linux, Windows and macOS.

| Project | Version | Adapter | Scenarios / steps |
| --- | --- | --- | --- |
| [pydantic/pydantic](https://github.com/pydantic/pydantic) | 2.14.1 | [pydantic](consumers/pydantic_model.py) | 3 / 9 |
| [pyeve/cerberus](https://github.com/pyeve/cerberus) | 1.3.8 | [cerberus](consumers/cerberus_validation.py) | 3 / 9 |
| [msgspec/msgspec](https://github.com/msgspec/msgspec) | 0.22.0 | [msgspec](consumers/msgspec_validation.py) | 3 / 9 |
| [python-jsonschema/jsonschema](https://github.com/python-jsonschema/jsonschema) | 4.26.0 | [jsonschema](consumers/jsonschema_validation.py) | 3 / 9 |
| [keleshev/schema](https://github.com/keleshev/schema) | 0.7.8 | [schema](consumers/schema_validation.py) | 3 / 9 |
| [python-jsonschema/referencing](https://github.com/python-jsonschema/referencing) | 0.37.0 | [referencing](consumers/references.py) | 3 / 12 |
| [holoviz/param](https://github.com/holoviz/param) | 2.4.2 | [param](consumers/parameters.py) | 3 / 10 |
| [ipython/traitlets](https://github.com/ipython/traitlets) | 5.16.1 | [traitlets](consumers/traits.py) | 3 / 9 |
| [pallets-eco/blinker](https://github.com/pallets-eco/blinker) | 1.9.0 | [blinker](consumers/blinker_signals.py) | 3 / 13 |
| [jfhbrook/pyee](https://github.com/jfhbrook/pyee) | 16.0.0 | [pyee](consumers/pyee_events.py) | 3 / 12 |
| [pyapp-kit/psygnal](https://github.com/pyapp-kit/psygnal) | 0.16.1 | [psygnal](consumers/psygnal_signals.py) | 3 / 9 |
| [nocarryr/python-dispatch](https://github.com/nocarryr/python-dispatch) | 0.2.3 | [python-dispatch](consumers/dispatch_properties.py) | 3 / 9 |
| [ReactiveX/RxPY](https://github.com/ReactiveX/RxPY) | 6.1.0 | [rxpy](consumers/rx_streams.py) | 3 / 14 |
| [pytransitions/transitions](https://github.com/pytransitions/transitions) | 0.9.3 | [transitions](consumers/transitions_machine.py) | 3 / 14 |
| [fgmacedo/python-statemachine](https://github.com/fgmacedo/python-statemachine) | 3.2.2 | [python-statemachine](consumers/state_machine.py) | 3 / 14 |
| [stefankoegl/python-json-patch](https://github.com/stefankoegl/python-json-patch) | 1.37 | [jsonpatch](consumers/json_patches.py) | 3 / 9 |
| [inveniosoftware/dictdiffer](https://github.com/inveniosoftware/dictdiffer) | 0.10.0 | [dictdiffer](consumers/dictionary_diffs.py) | 3 / 12 |
| [qlustered/deepdiff](https://github.com/qlustered/deepdiff) | 9.1.0 | [deepdiff](consumers/deep_diffs.py) | 3 / 12 |
| [mahmoud/glom](https://github.com/mahmoud/glom) | 25.12.0 | [glom](consumers/glom_paths.py) | 3 / 12 |
| [mahmoud/boltons](https://github.com/mahmoud/boltons) | 26.2.0 | [boltons](consumers/boltons_cache.py) | 3 / 16 |

## What these observations mean

- **pydantic:** Validated field assignment, rejected replacement and coercion on a fixed BaseModel. No model-level after validators, async validators or arbitrary schema input.
- **cerberus:** Normalization, defaults and error recovery using one Validator. A failed validation can still have a normalized document; no transaction guarantee.
- **msgspec:** Strict versus converting typed Struct validation, unknown keys and recovery. No assignment validation, binary codecs or performance comparison.
- **jsonschema:** Draft 2020-12 error paths, numeric type checks and defaults remaining annotations. No remote references or optional format plugins.
- **schema:** Native Use transformations, optional defaults and unknown-key rejection. No arbitrary callables supplied by a trace.
- **referencing:** Immutable Registry replacement, JSON pointers and missing-reference recovery. Only explicitly registered resources; no network retrieval.
- **param:** Native batching, discarded notifications and watcher removal. A batch retains the last Event.old, not necessarily the value before the batch.
- **traitlets:** Held notifications, rollback on TraitError and observer removal. This fixture covers bounded built-in traits, not arbitrary custom validators.
- **blinker:** Sender filtering, disconnect/reconnect and muted sends. Receiver lifetime is explicit; no multi-listener ordering or GC timing claim.
- **pyee:** Synchronous once removal before a reentrant emit, no-listener return values and unhandled error recovery. No asyncio, Trio or executor coverage.
- **psygnal:** Blocked versus paused signals, delivery after context exit, last-event reduction and disconnect. No Qt or threaded delivery.
- **python-dispatch:** Property equality, coalescing emission locks and unbind. One retained receiver; no assumption about listener ordering.
- **rxpy:** Debounce supersession, completion flush and disposal with TestScheduler virtual time. No sleeps, threads or real network timing.
- **transitions:** An original two-state draft fixture exercises native routing, guards and cancel. Callback-defined edit semantics are not built-in transitions features.
- **python-statemachine:** The same original synchronous draft fixture exercises native guards and invalid-state rejection. No async, threading, SCXML or diagram coverage.
- **jsonpatch:** Copy-mode failure preservation versus partial in-place writes, escaped pointers and list insertion. No invented rollback for in-place operations.
- **dictdiffer:** Native diff/patch/revert round trips for nested mappings, lists and empty diffs. No conflict detection or arbitrary Python objects.
- **deepdiff:** Native bidirectional Delta apply/subtract round trips. No serialized delta loading, pickle, performance claim or untrusted object deserialization.
- **glom:** Literal Path assignment/deletion, missing mappings and dotted-key isolation. No executable specs supplied through the protocol.
- **boltons:** Native LRU recency, eviction, overwrite and hit/miss counters. Snapshot observation does not itself access keys; no benchmark claim.

The small models, state machines and callbacks are original consumer fixtures.
They provide a workload for the library; they do not reimplement the library.
Parser failure is not assumed to preserve or restore arbitrary state. In
particular, JSON Patch copy mode and in-place mode intentionally have different
failure expectations, and Param and Traitlets preserve different old values in
batched notifications. The fixtures do not imply equivalence between libraries.

Input batches are checked in full before native writes or emissions begin.
Expected native validation errors are observable; unexpected exceptions terminate
the adapter and make the trace fail. No remote services, graphical interfaces,
assets or new Rust/Python FFI are involved.
