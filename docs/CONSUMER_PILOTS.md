# External consumer model pilots

These examples exercise real, separately pinned libraries through interaction-check. They are external experiments, not accepted upstream integrations or full application tests. Native controls remain alongside the JSON traces. No runtime dependency is proposed by these examples.

| Example | Pinned package | Passing traces / steps | Scope |
|---|---|---|---|
| [Cytoscape.js](../examples/cytoscape/README.md) | cytoscape 3.34.4 | 3 / 13 | Remove a node and its incident edge twice, restore selection, and restore a reversed edge. Observations come from real collections and add/remove/select events. |
| [Rete.js](../examples/rete/README.md) | rete 2.0.6 | 3 / 19 | Cancel noderemove, connectioncreate, and clear in a real NodeEditor pipe, then retry after lifting the veto. |
| [SurveyJS Form Library](../examples/surveyjs/README.md) | survey-core 3.2.2 | 3 / 16 | Reject navigation past a required question, clear a hidden answer, then complete, clear, and reuse a survey. |
| [TanStack Form](../examples/tanstack-form/README.md) | @tanstack/form-core 1.33.5 | 2 / 9 | Run normal form-level validation and reset after completion. A separate deterministic deferred-promise trace reproduces stale errors after reset while validation is pending. |
| [React Flow](../examples/xyflow/README.md) | @xyflow/react 12.12.0, react 19.2.0, react-dom 19.2.0 | 3 / 12 | Apply selection, position, and removal changes; ignore stale changes for a removed or unknown node. |
| [diagram-js](../examples/diagram-js/README.md) | diagram-js 15.28.1, didi 11.0.1 | 3 / 15 | Execute, undo, redo, reject, and branch commands using the real CommandStack, EventBus, and dependency injector. |
| [GrapesJS](../examples/grapesjs/README.md) | grapesjs 0.23.8, jsdom 30.1.3 | 3 / 15 | Rename a real component, undo/redo, preserve redo after an unchanged value, and replace redo with a new edit. |
| [Fabric.js](../examples/fabric/README.md) | fabric 7.4.0 | 3 / 11 | Move a real Group, detach and re-add objects, and preserve their scene centers. A detached object must not move with its former group. |
| [vee-validate](../examples/vee-validate/README.md) | vee-validate 4.15.1, vue 3.5.44 | 3 / 14 | Mount a null-rendering Vue component, validate an invalid value, correct it, and reset repeatedly. |
| [Excalidraw](../examples/excalidraw/README.md) | @excalidraw/excalidraw 0.18.1, @napi-rs/canvas 1.0.13, jsdom 30.1.3, react 18.3.1, react-dom 18.3.1 | 3 / 12 | Convert real elements, mutate coordinates, preserve versions on no-op changes, and restore saved/deleted geometry. |
| [PyQtGraph](../examples/pyqtgraph/README.md) | pyqtgraph 0.14.0, PyQt6 6.11.0, numpy 2.5.4 | 3 / 13 | Observe real parameter-tree notifications, batched changes, no-op writes, and save/restore with offscreen Qt. |
| [napari](../examples/napari/README.md) | napari 0.9.2, numpy 2.5.4 | 3 / 17 | Use real image layers and LayerList to remove selected unlocked layers, retain locked layers, and toggle visibility. |
| [Toga](../examples/toga/README.md) | toga-dummy 0.5.7 | 3 / 11 | Use the official dummy backend to observe real Selection data and callbacks through removal, clear, and append. |
| [Floem reactive](../examples/rust-consumers/README.md) | Git `1351ffb1` | 3 / 13 | Batch effects, unsubscribe a dynamic dependency, and recreate a disposed scope. |
| [Helix core](../examples/rust-consumers/README.md) | Git `ba40e547` | 3 / 15 | Invert Unicode transactions, select the latest history branch, and stop at history boundaries. |
| [Microsoft Edit](../examples/rust-consumers/README.md) | Git `cb6de0a8` | 3 / 15 | Restore dirty/clean markers through history and normalize CRLF before moving by UTF-8 byte offsets. |
| [Xilem Core](../examples/rust-consumers/README.md) | Git `271a27a6` | 3 / 20 | Rebuild an optional no-element view and reject messages for previous generations. |

| [Icy Draw engine](../examples/icy-draw/README.md) | Git `9ebe3dea`, edit-session `968ebd2f` | 3 / 23 | Stage a layer name, commit once through the host command, preserve Redo on no-op, and reject a stale draft after edit/undo. |
| [Eldiron text widget](../examples/eldiron/README.md) | Git `c1ac529b` | 3 / 14 | Paste Unicode, undo/redo, and clear native widget history with programmatic set_value. |

Windows local validation for the nineteen rows: 38 native/boundary tests, 56 passing traces / 277 steps, five shared Python transport tests, and two Rust protocol tests. The TanStack Form pending-reset trace is a separate known failure, not a passing test. Hosted CI must be checked independently.

SurveyJS has merged its own [survey-core/tester harness](https://github.com/surveyjs/survey-library/pull/11723). Prefer that project-specific tool for upstream scenarios; this external example is a comparison, not a request to add a competing dependency. Toga requires prior permission for unsolicited AI-assisted contributions.

[Amp](../examples/amp/README.md) is the twentieth implementation, compiled on Linux inside the pinned editor's own TestTerminal harness. Its native Unicode control and three normal traces / fourteen steps pass CI at `585f027`. The branch trace explicitly supplies Home after Undo. The original direct-insert failure is preserved and verified separately at step 4, not reported as an upstream fix or a GUI reproduction. Combined with the nineteen Windows-verified consumers, this gives 39 native/boundary tests and 59 normal traces / 291 steps. Nineteen Linux consumer jobs passed at `585f027`; Eldiron required an additional Wayland development package and must be checked on the next head.

The Icy Draw identity/generation fixture belongs to the adapter, not the upstream dialog. Eldiron covers the native text widget, not ProjectUndo or the rename dialog. The source pins and narrower model-only scope are documented in each README.
