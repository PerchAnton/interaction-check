# PyQtGraph parameter replay

This external example uses PyQtGraph 0.14.0 and real PyQt6 objects. It checks batched tree notifications, unchanged values, and save/restore of two integer parameters. It is not a visual test or an accepted upstream integration.

Use an isolated Python 3.12 environment:

```sh
python -m pip install -r examples/pyqtgraph/requirements.txt
python examples/verify_python_consumers.py pyqtgraph
```

The verifier runs a native control, an adapter boundary test, the shared transport tests, and three traces (13 steps). Qt uses its offscreen platform. The adapter observes real `sigTreeStateChanged` signals; it does not generate expected notifications. No runtime dependency or replacement for upstream's pytest suite is proposed.
