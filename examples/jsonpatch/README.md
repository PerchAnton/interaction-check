# JSON Patch failure behavior

These three scenarios call jsonpatch 1.39. One inserts a list item and updates
the key `a/b` through an escaped JSON Pointer. In the other two, a successful
replacement is followed by a failing `test`. Copy mode preserves the original
document. In-place mode retains the earlier write.

From the repository root, using an activated Python 3.12 virtual environment:

```sh
python -m pip install -r examples/jsonpatch/requirements.txt
python examples/jsonpatch/verify.py --report jsonpatch-report.json
```

The verifier runs the installed interaction-check 0.1.0b1 package in isolated
mode and checks the version in its report. Omit `--report` for a temporary
report. Run the native input check with
`python -m unittest discover -s examples/jsonpatch -p native_tests.py`.

The scenarios and input handling were extracted from [PR #14](https://github.com/PerchAnton/interaction-check/pull/14).
The [upstream tutorial](https://github.com/stefankoegl/python-json-patch/blob/v1.39/doc/tutorial.rst)
shows how to exercise copy and in-place behavior directly with the Python API.
