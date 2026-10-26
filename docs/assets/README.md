# README overview asset

`overview.svg` is an editable, self-contained vector graphic with system fonts,
explicit colors, a title and description. It contains no scripts, external fonts,
images or trackers. The repository README also provides accessible text and sources.

Snapshot: **26 October 2026**. Sources:

- [Validation](../VALIDATION.md): 41 runner tests and 6 focused Node tests.
- [PdfCraft state report](../evidence/pdfcraft-alpha4.json): 10 scenarios / 79 steps.
- [XState raw evidence](../evidence/xstate.json): 120 and 1 non-root lockfile package
  entries, 30 native/replay timing samples, and three controlled model mutations.
- [Value analysis](../VALUE.md): installation scope, source counts, method and limits.

Package bars share a zero-to-120 scale; the focused bar is exactly 1/120 of the full
width. Timing bars share a zero-to-200 ms scale and use the unrounded medians
74.6179165 and 183.928563 ms. The displayed numbers are rounded to one decimal place.
The ratio is rounded to two decimal places. These local timings include startup and
exclude installation and JSON report writing; replay is slower in this example.

When new measurements are available, update the SVG, README table and snapshot date
together. Retain raw data, label package scope and show the native baseline even if
it performs better. Render the SVG at README width to check labels and contrast.
The CI badges update automatically; these measurement counts do not.

`pyee-coverage.svg` supplements the overview with the native-test audit dated
26 October 2026. Its source is [the four-run report](../evidence/pyee/results.json):
53 baseline tests pass, 54 with the candidate pass; after one deliberate mutation,
the original 53 still pass and only the candidate fails. It shows discrete outcomes,
not a percentage or speed comparison. Scope, test and reproduction are in the
[pyee audit](../../examples/pyee/README.md). These counts are separate from runner tests.
