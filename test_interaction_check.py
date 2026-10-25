import json
import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

from interaction_check import (CheckError, MAX_DEPTH, differences, replay, strict_json,
                               validate, main, write_report)


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
        return [sys.executable, "-X", "utf8", "-c", code]

    def test_real_subprocess_and_unicode_roundtrip(self):
        self.assertTrue(replay(scenario(), self.adapter(ECHO))["passed"])

    def test_unicode_line_separators_inside_json_are_not_record_boundaries(self):
        case = scenario()
        for separator in ["\u0085", "\u2028", "\u2029"]:
            value = f"first{separator}second"
            case["steps"][0] = {"event": {"text": value}, "expect": {"text": value}}
            raw_unicode_echo = ECHO.replace('r["event"]})', 'r["event"]}, ensure_ascii=False)')
            with self.subTest(separator=repr(separator)):
                self.assertTrue(replay(case, self.adapter(raw_unicode_echo))["passed"])

    def test_jsonl_accepts_lf_crlf_and_optional_final_newline(self):
        line = json.dumps({"protocol": 1, "id": 1, "state": scenario()["steps"][0]["event"]})
        for ending in ["", "\n", "\r\n"]:
            with self.subTest(ending=repr(ending)):
                code = f"import sys; sys.stdout.buffer.write({(line + ending).encode()!r})"
                self.assertTrue(replay(scenario(), self.adapter(code))["passed"])
        with self.assertRaisesRegex(CheckError, "Expected 1 replies, got 2"):
            replay(scenario(), self.adapter(ECHO + "print()"))

    def test_partial_nested_objects_and_exact_array_length_and_order(self):
        self.assertEqual(differences({"a": {"b": 1}}, {"a": {"b": 1, "c": 2}}), [])
        self.assertEqual(differences([{"b": 1}], [{"b": 1, "c": 2}]), [])
        self.assertTrue(differences([1, 2], [2, 1]))
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

    def test_json_nesting_limit_and_parser_recursion_fail_cleanly(self):
        strict_json("[" * MAX_DEPTH + "0" + "]" * MAX_DEPTH)
        for depth in [MAX_DEPTH + 1, 20000]:
            with self.subTest(depth=depth), self.assertRaises(CheckError):
                strict_json("[" * depth + "0" + "]" * depth)

    def test_deep_adapter_response_identifies_step(self):
        response = '{"protocol":1,"id":1,"state":{"deep":' + "[" * MAX_DEPTH + "0" + "]" * MAX_DEPTH + '}}'
        with self.assertRaisesRegex(CheckError, r"Step 1: JSON nesting"):
            replay(scenario(), self.adapter(f"print({response!r})"))

    def test_python_api_rejects_cycles_and_non_json_values(self):
        cyclic = []
        cyclic.append(cyclic)
        for value in [cyclic, float("nan"), (1, 2), {1: "not a string key"}, "\ud800"]:
            case = scenario()
            case["steps"][0]["event"]["extra"] = value
            with self.subTest(value_type=type(value).__name__), self.assertRaises(CheckError):
                replay(case, self.adapter(ECHO))

    def test_unpaired_surrogates_are_rejected_in_keys_and_values(self):
        for value in [r'"\ud800"', r'{"\udfff": 1}']:
            with self.subTest(value=value), self.assertRaisesRegex(CheckError, "Unicode"):
                strict_json(value)

    def test_invalid_duplicate_key_still_produces_a_cli_failure_report(self):
        with tempfile.TemporaryDirectory() as root:
            case, report = Path(root) / "case.json", Path(root) / "report.json"
            case.write_text(r'{"\ud800": 1, "\ud800": 2}', encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, "-X", "utf8", str(Path(__file__).with_name("interaction_check.py")),
                 "--report", str(report), str(case), "--", *self.adapter(ECHO)],
                capture_output=True, text=True, encoding="utf-8", timeout=10, check=False)
            self.assertEqual(completed.returncode, 1)
            self.assertNotIn("Traceback", completed.stderr)
            result = json.loads(report.read_text(encoding="utf-8"))["results"][0]
            self.assertFalse(result["passed"])
            self.assertIn("Duplicate JSON key", result["error"])

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

    def test_json_and_junit_reports_keep_names_sources_and_failures(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            cases = [root / name for name in ["pass.json", "fail.json", "broken.json"]]
            first = dict(scenario(), name='Україна <preview> & "reset"')
            second = dict(scenario(), name="wrong expectation")
            second["steps"][0]["expect"]["text"] = "wrong"
            cases[0].write_text(json.dumps(first), encoding="utf-8")
            cases[1].write_text(json.dumps(second), encoding="utf-8")
            cases[2].write_text("{broken", encoding="utf-8")
            report, junit = root / "report.json", root / "junit.xml"
            code = "import sys; sys.stderr.write('diagnostic\\x01 <&>')\n" + ECHO
            with contextlib.redirect_stdout(io.StringIO()):
                status = main(["--report", str(report), "--junit", str(junit),
                               *map(str, cases), "--", *self.adapter(code)])
            self.assertEqual(status, 1)
            results = json.loads(report.read_text(encoding="utf-8"))["results"]
            self.assertEqual([r["name"] for r in results], [first["name"], second["name"], "broken.json"])
            self.assertEqual([r["source"] for r in results], list(map(str, cases)))
            self.assertEqual([r["passed"] for r in results], [True, False, False])
            suite = ET.parse(junit).getroot()
            self.assertEqual(suite.attrib["tests"], "3")
            self.assertEqual(suite.attrib["failures"], "2")
            tests = suite.findall("testcase")
            self.assertEqual(tests[0].attrib["name"], first["name"])
            self.assertEqual(tests[0].find("system-err").text, "diagnostic\ufffd <&>")
            self.assertIsNone(tests[0].find("failure"))
            self.assertIn("state.text", tests[1].find("failure").text)
            self.assertIsNotNone(tests[2].find("failure"))

    def test_successful_junit_report_and_replacing_existing_report(self):
        with tempfile.TemporaryDirectory() as root:
            case, report = Path(root) / "case.json", Path(root) / "report.xml"
            case.write_text(json.dumps(scenario()), encoding="utf-8")
            report.write_text("old report", encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()):
                status = main(["--junit", str(report), str(case), "--", *self.adapter(ECHO)])
            self.assertEqual(status, 0)
            self.assertEqual(ET.parse(report).getroot().attrib["failures"], "0")
            self.assertEqual(set(Path(root).iterdir()), {case, report})

    def test_report_write_errors_fail_without_tracebacks_and_other_report_is_written(self):
        with tempfile.TemporaryDirectory() as root:
            case, good_report = Path(root) / "case.json", Path(root) / "junit.xml"
            case.write_text(json.dumps(scenario()), encoding="utf-8")
            for bad_report in [Path(root), Path(root) / "missing" / "report.json"]:
                stderr = io.StringIO()
                with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
                    status = main(["--report", str(bad_report), "--junit", str(good_report),
                                   str(case), "--", *self.adapter(ECHO)])
                self.assertEqual(status, 1)
                self.assertIn("ERROR writing report", stderr.getvalue())
                self.assertNotIn("Traceback", stderr.getvalue())
                self.assertEqual(ET.parse(good_report).getroot().attrib["failures"], "0")
            self.assertEqual(set(Path(root).iterdir()), {case, good_report})

    def test_report_path_aliases_are_rejected_before_running_adapter(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            case, hardlink, report = root / "case.json", root / "hardlink.json", root / "out.json"
            original = json.dumps(scenario())
            case.write_text(original, encoding="utf-8")
            os.link(case, hardlink)
            for options in [["--report", str(case)], ["--junit", str(hardlink)],
                            ["--report", str(report), "--junit", str(report)]]:
                with self.subTest(options=options), mock.patch("interaction_check.subprocess.run") as run:
                    with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                        main([*options, str(case), "--", *self.adapter(ECHO)])
                    self.assertEqual(error.exception.code, 2)
                    run.assert_not_called()
            self.assertEqual(case.read_text(encoding="utf-8"), original)

    def test_failed_atomic_replace_preserves_old_report_and_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as root:
            report = Path(root) / "report.json"
            report.write_text("old", encoding="utf-8")
            with mock.patch("interaction_check.os.replace", side_effect=OSError("disk error")):
                with self.assertRaises(OSError):
                    write_report(report, "new")
            self.assertEqual(report.read_text(encoding="utf-8"), "old")
            self.assertEqual(list(Path(root).iterdir()), [report])

    def test_stdout_protocol_is_separate_from_stderr(self):
        result = replay(scenario(), self.adapter("import sys; print('diagnostic', file=sys.stderr)\n" + ECHO))
        self.assertIn("diagnostic", result["stderr"])


if __name__ == "__main__":
    unittest.main()
