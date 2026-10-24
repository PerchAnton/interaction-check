import json
import contextlib
import io
from pathlib import Path
import sys
import tempfile
import unittest

from interaction_check import CheckError, differences, replay, strict_json, validate, main


def scenario():
    return {"schema": 1, "name": "minimal", "steps": [
        {"event": {"text": "Україна e\u0301 👩‍💻"}, "expect": {"text": "Україна e\u0301 👩‍💻"}}
    ]}


ECHO = '''import json, sys
for line in sys.stdin:
    r = json.loads(line)
    assert "expect" not in r
    print(json.dumps({"protocol": 1, "id": r["id"], "state": r["event"]}))
'''


class Tests(unittest.TestCase):
    def adapter(self, code):
        return [sys.executable, "-c", code]

    def test_real_subprocess_and_unicode_roundtrip(self):
        self.assertTrue(replay(scenario(), self.adapter(ECHO))["passed"])

    def test_partial_nested_object_but_exact_array(self):
        self.assertEqual(differences({"a": {"b": 1}}, {"a": {"b": 1, "c": 2}}), [])
        self.assertTrue(differences([1], [1, 2]))
        self.assertTrue(differences([True], [1]))

    def test_missing_null_is_not_present_null(self):
        self.assertTrue(differences({"a": None}, {}))
        self.assertEqual(differences({"a": None}, {"a": None}), [])

    def test_bool_is_not_number(self):
        self.assertTrue(differences(True, 1))
        self.assertTrue(differences(0, False))

    def test_failure_points_to_step_and_field(self):
        case = scenario()
        case["steps"][0]["expect"]["text"] = "wrong"
        with self.assertRaisesRegex(CheckError, r"Step 1 .*state.text"):
            replay(case, self.adapter(ECHO))

    def test_exit_failure_is_not_hidden_by_matching_output(self):
        with self.assertRaisesRegex(CheckError, "exited with 7"):
            replay(scenario(), self.adapter(ECHO + "raise SystemExit(7)"))

    def test_timeout_terminates_stalled_adapter(self):
        with self.assertRaisesRegex(CheckError, "timed out"):
            replay(scenario(), self.adapter("import time; time.sleep(5)"), 0.05)

    def test_wrong_id_is_rejected(self):
        with self.assertRaisesRegex(CheckError, "mismatched reply id"):
            replay(scenario(), self.adapter(ECHO.replace('r["id"]', '999')))

    def test_invalid_and_missing_output(self):
        for code in ["print('not json')", "pass", "print('{}\\n{}')"]:
            with self.subTest(code=code), self.assertRaises(CheckError):
                replay(scenario(), self.adapter(code))

    def test_non_finite_json_is_rejected(self):
        for text in ['NaN', '{"v": Infinity}', '[-Infinity]', '{"v": 1e999}']:
            with self.subTest(text=text), self.assertRaises(CheckError):
                strict_json(text)

    def test_duplicate_json_keys_are_rejected(self):
        with self.assertRaisesRegex(CheckError, "Duplicate JSON key"):
            strict_json('{"schema": 1, "schema": 2}')

    def test_empty_or_ambiguous_scenarios_rejected(self):
        cases = [dict(scenario(), schema=True), dict(scenario(), steps=[]),
                 dict(scenario(), steps=[{"event": {}, "expect": {}}]),
                 dict(scenario(), steps=[{"event": {}, "expect": {"a": 1}, "exepct": {}}])]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(CheckError):
                validate(case)

    def test_non_finite_timeout(self):
        for timeout in [0, -1, float("inf"), float("nan")]:
            with self.subTest(timeout=timeout), self.assertRaises(CheckError):
                replay(scenario(), self.adapter(ECHO), timeout)

    def test_report_and_failure_exit_status(self):
        with tempfile.TemporaryDirectory() as root:
            case = Path(root) / "scenario.json"
            report = Path(root) / "report.json"
            case.write_text(json.dumps(scenario()), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                status = main(["--report", str(report), str(case), "--", *self.adapter("pass")])
            self.assertEqual(status, 1)
            self.assertFalse(json.loads(report.read_text())["results"][0]["passed"])

    def test_stdout_protocol_is_separate_from_stderr(self):
        result = replay(scenario(), self.adapter("import sys; print('diagnostic', file=sys.stderr)\n" + ECHO))
        self.assertIn("diagnostic", result["stderr"])


if __name__ == "__main__":
    unittest.main()
