"""Console encoding must not determine JSON results or adapter input decoding."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent
TEXT = "Україна e\u0301 👩‍💻"
ECHO = '''import json, sys
for line in sys.stdin.buffer:
    request = json.loads(line.decode("utf-8"))
    print(json.dumps({"protocol": 1, "id": request["id"], "state": request["event"]}))
'''


class ConsoleEncodingTests(unittest.TestCase):
    def run_cli(self, root, encoding, *, mismatch=False):
        scenario = {
            "schema": 1,
            "name": "mismatch" if mismatch else TEXT,
            "steps": [{"event": {"text": TEXT},
                       "expect": {"text": "Друге" if mismatch else TEXT}}],
        }
        source = root / "case.json"
        source.write_text(json.dumps(scenario, ensure_ascii=False), encoding="utf-8")
        exports = root / "failures-界"
        command = [sys.executable, str(ROOT / "interaction_check.py"),
                   "--report", str(root / "report.json"), "--trace",
                   "--junit", str(root / "report.xml")]
        if mismatch:
            command += ["--failure-dir", str(exports)]
        command += [str(source), "--", sys.executable, "-c", ECHO]
        result = subprocess.run(
            command, env=dict(os.environ, PYTHONIOENCODING=encoding, PYTHONUTF8="0"),
            capture_output=True, timeout=10, check=False,
        )
        self.assertEqual(result.returncode, int(mismatch), result.stderr)
        self.assertNotIn(b"Traceback", result.stderr)
        self.assertTrue((root / "report.json").is_file(), result.stderr)
        document = json.loads((root / "report.json").read_text(encoding="utf-8"))
        item, = document["results"]
        self.assertEqual(item["name"], scenario["name"])
        self.assertEqual(item["passed"], not mismatch)
        self.assertEqual(item["trace"][0]["actual"]["text"], TEXT)
        self.assertEqual(item["trace"][0]["expect"], scenario["steps"][0]["expect"])
        suite = ET.parse(root / "report.xml").getroot()
        self.assertEqual(suite.attrib["failures"], str(int(mismatch)))
        self.assertEqual(suite.find("testcase").attrib["name"], scenario["name"])
        output = result.stdout.decode(encoding)
        if mismatch:
            exported = json.loads((exports / "0001.json").read_text(encoding="utf-8"))
            self.assertEqual(exported, scenario)
            self.assertIn("Step 1", output)
            expected_path = str(exports / "0001.json").encode(
                encoding, errors="backslashreplace").decode(encoding)
            self.assertIn(expected_path, output)
        else:
            expected_name = TEXT.encode(encoding, errors="backslashreplace").decode(encoding)
            self.assertIn("PASS " + expected_name, output)

    def test_unicode_names_keep_pass_status_and_reports(self):
        for encoding in ("ascii", "cp1252", "utf-8"):
            with self.subTest(encoding=encoding), tempfile.TemporaryDirectory() as directory:
                self.run_cli(Path(directory), encoding)

    def test_unicode_mismatch_and_export_path_keep_failure_evidence(self):
        for encoding in ("ascii", "cp1252", "utf-8"):
            with self.subTest(encoding=encoding), tempfile.TemporaryDirectory() as directory:
                self.run_cli(Path(directory), encoding, mismatch=True)

    def test_quickstart_decodes_protocol_as_utf8_regardless_of_console_encoding(self):
        events = [{"op": "open"}, {"op": "type", "text": TEXT}, {"op": "save"}]
        payload = "".join(json.dumps({"protocol": 1, "id": index, "event": event},
                                     ensure_ascii=False) + "\n"
                          for index, event in enumerate(events, 1)).encode("utf-8")
        for encoding in ("ascii", "cp1252", "utf-8"):
            with self.subTest(encoding=encoding):
                result = subprocess.run(
                    [sys.executable, "-B", str(ROOT / "examples/quickstart/adapter.py")],
                    input=payload, capture_output=True, timeout=10, check=False,
                    env=dict(os.environ, PYTHONIOENCODING=encoding, PYTHONUTF8="0"),
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                replies = [json.loads(line) for line in result.stdout.decode("utf-8").splitlines()]
                self.assertEqual(len(replies), len(events))
                self.assertEqual(replies[-1]["state"]["saved"], TEXT)


if __name__ == "__main__":
    unittest.main()
