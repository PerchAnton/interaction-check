# napari layer-list replay

This external example uses napari 0.9.2 and real `LayerList`/`Image` objects with two tiny NumPy arrays. It checks selection, locked-layer removal, and visibility. It does not construct a viewer, render images, or test GPU/backend behavior.

Use an isolated Python 3.12 environment:

```sh
python -m pip install -r examples/napari/requirements.txt
python examples/verify_python_consumers.py napari
```

The verifier runs a native control, an adapter boundary test, the shared transport tests, and three traces (17 steps). `NAPARI_CONFIG` is empty to avoid reading or saving user settings. napari may create its normal built-in icon cache on first import. Layer locks are normalized to booleans because these fixtures use only the all/none lock states.

This is a model-level experiment, not an accepted upstream integration. Existing upstream pytest coverage remains the authority for the model. The optional JSON reports offer a portable sequence and step-level failure report, not new evidence of a rendering bug.
