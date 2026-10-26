"""Replay evidence must describe observed states without changing adapter input."""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

from interaction_check import CheckError, main, replay


ECHO = '''import json, sys
for line in sys.stdin:
    request = json.loads(line)
    assert set(request) == {"protocol", "id", "event"}
    print(json.dumps({"protocol": 1, "id": request["id"], "state": request["event"]}))
'''


def case():
    return {"schema": 1, "name": "observable steps", "steps": [
        {"event": {"text": "first", "extra": 1}, "expect": {"text": "first"}},
        {"event": {"text": "界🙂", "extra": None}, "expect": {"text": "界🙂"}},
        {"event": {"text": "last"}, "expect": {"text": "last"}},
    ]}


class TraceTests(unittest.TestCase):
    def command(self, code=ECHO):
        return [sys.executable, "-X", "utf8", "-c", code]

    def test_default_report_stays_compact(self):
        self.assertNotIn("trace", replay(case(), self.command()))

    def test_trace_keeps_observed_fields_and_unicode_without_sending_expectations(self):
        result = replay(case(), self.command(), trace=True)
        self.assertEqual(len(result["trace"]), 3)
        self.assertEqual(result["trace"][1], {
            "step": 2, "event": {"text": "界🙂", "extra": None},
            "expect": {"text": "界🙂"}, "actual": {"text": "界🙂", "extra": None},
            "passed": True,
        })

    def test_mismatch_retains_prefix_and_failed_state_but_not_unchecked_tail(self):
        scenario = case()
        scenario["steps"][1]["expect"] = {"text": "wrong", "missing": None}
        with self.assertRaises(CheckError) as caught:
            replay(scenario, self.command(), trace=True)
        evidence = caught.exception.trace
        self.assertEqual([entry["step"] for entry in evidence], [1, 2])
        self.assertTrue(evidence[0]["passed"])
        self.assertFalse(evidence[1]["passed"])
        self.assertNotIn("missing", evidence[1]["actual"])
        self.assertEqual(evidence[1]["expect"]["missing"], None)
        self.assertEqual(len(evidence[1]["differences"]), 2)

    def test_protocol_failure_does_not_invent_an_observed_state(self):
        bad = ECHO.replace('request["id"], "state"', '(99 if request["id"] == 2 else 1), "state"')
        with self.assertRaisesRegex(CheckError, "Step 2") as caught:
            replay(case(), self.command(bad), trace=True)
        self.assertEqual(len(caught.exception.trace), 1)
        self.assertTrue(caught.exception.trace[0]["passed"])

    def test_crash_does_not_publish_unvalidated_output_as_a_trace(self):
        with self.assertRaisesRegex(CheckError, "exited with 7") as caught:
            replay(case(), self.command(ECHO + "raise SystemExit(7)"), trace=True)
        self.assertIsNone(caught.exception.trace)

    def test_cli_writes_evidence_on_failure_and_continues(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            scenario = case()
            scenario["steps"][1]["expect"]["text"] = "wrong"
            bad, good, report, junit = [root / name for name in
                                       ["bad.json", "good.json", "report.json", "report.xml"]]
            bad.write_text(json.dumps(scenario), encoding="utf-8")
            good.write_text(json.dumps(case()), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                code = main(["--trace", "--report", str(report), "--junit", str(junit),
                             str(bad), str(good), "--", *self.command()])
            results = json.loads(report.read_text(encoding="utf-8"))["results"]
            self.assertEqual(code, 1)
            self.assertEqual([r["passed"] for r in results], [False, True])
            self.assertEqual([len(r["trace"]) for r in results], [2, 3])
            self.assertIn("Step 2", junit.read_text(encoding="utf-8"))

    def test_cli_trace_requires_json_report(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            main(["--trace", "unused.json", "--", *self.command()])
        self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
