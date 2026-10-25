# PdfCraft Document Properties adapter

The implementation is owned by the PdfCraft consumer in [PR #4594](https://github.com/storytold/pdfcraft/pull/4594):

- [Real UI adapter](https://github.com/PerchAnton/pdfcraft/blob/535d990d10832baf3b0a64910c51b280c224bd5c/crates/ui-egui/examples/properties_scenarios.rs)
- [Ten scenarios](https://github.com/PerchAnton/pdfcraft/tree/535d990d10832baf3b0a64910c51b280c224bd5c/tests/interactions/document-properties)
- [Integration and protocol notes](https://github.com/PerchAnton/pdfcraft/blob/535d990d10832baf3b0a64910c51b280c224bd5c/docs/document-properties-sessions.md)

This directory is the entry point from interaction-check. The Rust adapter and scenarios
live together in PdfCraft, so they compile against its real UI, engine and workspace
vendored patches. No duplicate external Cargo patch table or copied UI is maintained here.

From a checkout of interaction-check, with Rust 1.99.1 and Python 3.10+:

```sh
git clone https://github.com/PerchAnton/pdfcraft ../pdfcraft
git -C ../pdfcraft checkout 535d990d10832baf3b0a64910c51b280c224bd5c
cargo build --locked -j 2 --manifest-path ../pdfcraft/Cargo.toml \
  -p pdfcraft-ui-egui --example properties_scenarios
mkdir -p reports/local
PDFCRAFT_SYSTEM_FONTS=0 PDFCRAFT_LOCALE=en-US \
  python3 interaction_check.py --timeout 30 \
  --report reports/local/pdfcraft.json --junit reports/local/pdfcraft.xml \
  ../pdfcraft/tests/interactions/document-properties/*.json -- \
  ../pdfcraft/target/debug/examples/properties_scenarios
```

Use an unused sibling path; an existing checkout need not be replaced. On Windows the
executable ends in `.exe`, and environment variables use the shell's syntax.
For exact runner reproduction, check out `7722d66c0ede7855ff58d1df3d1632fd4e5e66a5` in a
separate copy. The consumer pins edit-session to `033f7c3a67b825b8f222288788cc61234c0c945d`.

Typing and clicking use `egui_kittest` and actual controls. External changes, reload and
save/reopen use the real engine. Fixtures are generated two-page PDFs. Ordinary replay
needs no GPU; optional `--artifacts DIR` after the adapter executable renders screenshots
and writes the saved PDF, requiring a GPU/software renderer. Run one scenario at a time
for artifacts, with system-font fallback disabled. Keep generated files local.

The [local report](../../reports/pdfcraft-properties.json) records ten passing scenarios,
79 event/reply steps on macOS arm64. [Validation](../../docs/VALIDATION.md) records the
broader scoped checks and limits. No app runs a new server or needs Python at runtime.
Both independent projects remain experimental, dual-licensed MIT OR Apache-2.0;
upstream adoption and the proposed source exception are pending maintainer review.
