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

Windows local validation: 20 native/boundary tests, 29 passing traces / 136 steps. The TanStack Form pending-reset trace is a separate known failure, not a passing test. Hosted CI must be checked independently.

These are the first ten implementations from the 20-project investigation. The remaining projects are not implemented by this change.
