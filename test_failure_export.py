"""Failure exports must replay the checked prefix without changing expectations."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

import interaction_check as runner
from test_trace_report import ECHO, case


def adapter(code=ECHO):
    return [sys.executable, "-X", "utf8", "-c", code]


class FailureExportTests(unittest.TestCase):
    def run_case(self, root, scenario, *, command=None, options=()):
        source = root / "source.json"
        source.write_text(json.dumps(scenario, ensure_ascii=False), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            code = runner.main(["--failure-dir", str(root / "failures"), *options,
                                str(source), "--", *(command or adapter())])
        return code, source

    def test_export_preserves_expected_prefix_and_reproduces_same_mismatch(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            scenario = case()
            scenario["description"] = "保持 metadata"
            scenario["steps"][1]["expect"]["text"] = "expected, not observed"
            report = root / "report.json"
            code, source = self.run_case(root, scenario, options=("--report", str(report)))
            self.assertEqual(code, 1)
            exported = root / "failures" / "0001.json"
            prefix = json.loads(exported.read_text(encoding="utf-8"))
            self.assertEqual(prefix, dict(scenario, steps=scenario["steps"][:2]))
            self.assertEqual(json.loads(source.read_text(encoding="utf-8")), scenario)
            with self.assertRaisesRegex(runner.CheckError, "Step 2"):
                runner.replay(prefix, adapter())
            result = json.loads(report.read_text(encoding="utf-8"))["results"][0]
            self.assertEqual(result["failure_scenario"], str(exported))
            self.assertNotIn("trace", result)

    def test_passing_case_creates_no_failure_scenario(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            code, _ = self.run_case(root, case())
            self.assertEqual(code, 0)
            self.assertEqual(list((root / "failures").iterdir()), [])

    def test_protocol_crash_and_invalid_input_do_not_invent_a_prefix(self):
        commands = [adapter('print("not json")'),
                    adapter(ECHO + "raise SystemExit(7)")]
        for command, scenario in [(c, case()) for c in commands] + [(None, {"schema": 7})]:
            with self.subTest(command=command), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                code, _ = self.run_case(root, scenario, command=command)
                self.assertEqual(code, 1)
                self.assertEqual(list((root / "failures").iterdir()), [])

    def test_same_filename_and_scenario_name_get_distinct_exports(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            inputs = []
            for name in ["a", "b"]:
                (root / name).mkdir()
                source = root / name / "same.json"
                scenario = case()
                scenario["steps"][0]["expect"]["text"] = name
                source.write_text(json.dumps(scenario), encoding="utf-8")
                inputs.append(str(source))
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(runner.main(["--failure-dir", str(root / "out"),
                                               *inputs, "--", *adapter()]), 1)
            exports = sorted((root / "out").glob("*.json"))
            self.assertEqual([p.name for p in exports], ["0001.json", "0002.json"])
            self.assertEqual([json.loads(p.read_text())["steps"][0]["expect"]["text"]
                              for p in exports], ["a", "b"])

    def test_existing_directory_is_rejected_before_adapter_runs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "failures").mkdir()
            marker = root / "failures" / "keep.txt"
            marker.write_text("keep", encoding="utf-8")
            with patch.object(runner, "run_adapter") as run, \
                    contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
                self.run_case(root, case())
            self.assertEqual(caught.exception.code, 2)
            run.assert_not_called()
            self.assertEqual(marker.read_text(), "keep")

    def test_report_cannot_overwrite_export_or_its_directory(self):
        for report_name in ["failures", "failures/0001.json"]:
            with self.subTest(report=report_name), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                with patch.object(runner, "run_adapter") as run, \
                        contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    self.run_case(root, case(), options=("--report", str(root / report_name)))
                run.assert_not_called()
                self.assertFalse((root / "failures").exists())

    def test_export_write_failure_is_reported_without_claiming_a_saved_file(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            scenario = case()
            scenario["steps"][0]["expect"]["text"] = "mismatch"
            report = root / "report.json"
            write_report = runner.write_report

            def fail_export(path, content):
                if path.parent.name == "failures":
                    raise OSError("disk full")
                return write_report(path, content)

            with patch.object(runner, "write_report", side_effect=fail_export), \
                    contextlib.redirect_stderr(io.StringIO()):
                code, _ = self.run_case(root, scenario, options=("--report", str(report)))
            result = json.loads(report.read_text())["results"][0]
            self.assertEqual(code, 1)
            self.assertIn("disk full", result["export_error"])
            self.assertNotIn("failure_scenario", result)

    def test_cli_help_and_version_do_not_require_an_adapter(self):
        for option in ["--version", "--help"]:
            with self.subTest(option=option), contextlib.redirect_stdout(io.StringIO()), \
                    self.assertRaises(SystemExit) as caught:
                runner.main([option])
            self.assertEqual(caught.exception.code, 0)
