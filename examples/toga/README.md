# Toga selection replay

This external example uses Toga 0.5.7 and its official `toga-dummy` backend. It checks a real `Selection` widget's data and change callbacks when selecting, removing, clearing, and appending items. It does not test native Windows/macOS/GTK widgets.

Use an isolated Python 3.12 environment:

```sh
python -m pip install -r examples/toga/requirements.txt
python examples/verify_python_consumers.py toga
```

The verifier runs a native control, an adapter boundary test, the shared transport tests, and three traces (11 steps). No expected state is passed to the adapter.

This is an external experiment, not an upstream contribution or adoption. BeeWare's contribution policy requires prior permission for unsolicited AI-assisted contributions. This example does not imply that permission was obtained, and it does not replace Toga's own test suite.
