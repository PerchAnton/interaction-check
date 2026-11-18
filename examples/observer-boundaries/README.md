# Observer boundaries: values, subscriptions and notifications

These small consumers answer specific upstream questions using installed libraries.
A changed value, a callback in the current step, and the accumulated callback log
are separate observations. No full upstream test suite or adoption is claimed.

```sh
python -m pip install -r examples/observer-boundaries/requirements.txt
npm --prefix examples/observer-boundaries ci --ignore-scripts
node --test examples/observer-boundaries/native.test.mjs
python examples/observer-boundaries/native_test.py
python examples/observer-boundaries/verify.py --output artifacts/observer-boundaries
```

| Consumer | Observed result | Relevant discussion |
| --- | --- | --- |
| tiny-emitter 2.1.0 | Removing an unknown callback preserves both listeners; duplicate cleanup preserves the other listener; `once` can be removed with the original function | [#48](https://github.com/scottcorgan/tiny-emitter/issues/48) |
| PubSubJS 1.9.5 | Clearing `enter` also removes `entering`, with both clearing methods and with/without a direct parent subscription | [#215](https://github.com/mroderick/PubSubJS/issues/215), existing [fix #232](https://github.com/mroderick/PubSubJS/pull/232) |
| Atom 0.14.1 | Replacing `pos` changes its value without a `pos.x` callback. The old object is detached; subsequent changes to the replacement do notify. Observing both `pos` and `pos.x` reports the replacement once and tracks the new point | [#245](https://github.com/nucleic/atom/issues/245) |
| Traits 7.3.0 | A nested ReadOnly value and its square change. The direct observer fires, but the dependent property's callback does not | [#1735](https://github.com/enthought/traits/issues/1735) |
| Automat 25.4.16 | After the data factory fails, the next public `read()` hits a data-type assertion; the successful-factory control works | [#160](https://github.com/glyph/automat/issues/160), existing [proposal #177](https://github.com/glyph/automat/pull/177) |

The native checks retain the published discrepancies explicitly. The four JSON
reports contain **two passes and two failures**: Atom's requested replacement
notification first differs at step 2, and Traits' dependent callback first differs
at step 1. The Atom expectation is the behavior proposed in the discussion, not
a claim that its current API promises a synthetic nested notification. The
separate rebinding scenario confirms that tracking the new object does work.

For these narrow upstream questions, the native tests are sufficient. The optional
interaction-check runner adds a shared JSON scenario and first-difference report
when a consumer wants to compare adapters. It does not measure dispatch latency,
rendering, observer performance, or all semantics of these libraries.

## Comparing existing fixes

An independent check of PubSubJS #232 at `a01789839c6bacbc212478dc0b93c5f7a8c73a88`
preserves `entering` in all four cases while clearing `enter` and its children.
An independent check of Automat #177 at `13bc349781c44f4c1a6618fb5b3bd8ef901ebac7`
recovers from `ValueError` and a direct `BaseException` subclass **when an explicit
error state is configured**. With no configured error state, the same later
assertion remains. That design question is still open; the proposal is not
reported as fixing every factory-error path.

To repeat those comparisons, obtain the exact commits above. Pass PubSubJS's
`src/pubsub.js` saved as a `.cjs` file with `--pubsub-fixed PATH`, and Automat's
complete `src` directory with `--automat-source PATH`. The caller must retain
source hashes and commit identities; package metadata alone does not prove them.
The published baselines stay installed, and separate subprocesses load Automat's
source comparison. These are bounded checks, not the upstream complete suites.
