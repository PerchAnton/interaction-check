// Observe native parser output without comparing library-specific error prose.
export function validationState(state) {
  return {
    ...state,
    keys:
      state.output && typeof state.output === "object"
        ? Object.keys(state.output).sort()
        : [],
    inputUnchanged: JSON.stringify(state.input) === JSON.stringify(state.after),
  };
}
