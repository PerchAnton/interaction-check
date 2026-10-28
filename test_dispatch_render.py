import copy
import json
from pathlib import Path
import unittest

from examples.dispatch.render import render


class DispatchRenderTests(unittest.TestCase):
    def setUp(self):
        case = json.loads(Path("examples/dispatch/scenario.json").read_text(encoding="utf-8"))
        self.result = {"trace": [dict(s, actual=copy.deepcopy(s["expect"]), step=i, passed=True)
                                  for i, s in enumerate(case["steps"], 1)]}

    def test_distinguishes_writes_delta_log_and_property(self):
        text = render(self.result)
        self.assertIn("| 2 | writes [2, 3, 4]; lock on | [4] | [1, 4] | 4 | pass |", text)
        self.assertIn("| 5 | writes [5]; lock off | [] | [1, 4] | 5 | pass |", text)
        self.assertEqual(text.count("sequenceDiagram"), 2)

    def test_partial_expectations_and_reset_logs_are_not_invented(self):
        for change in [lambda t: t[1]["expect"].pop("log"),
                       lambda t: t[1]["actual"].update(log=[]),
                       lambda t: t[1]["actual"].update(count=True)]:
            result = copy.deepcopy(self.result)
            change(result["trace"])
            with self.assertRaises(ValueError):
                render(result)

    def test_only_checked_prefix_and_both_sides_of_mismatch(self):
        self.result["trace"] = self.result["trace"][:2]
        self.result["trace"][1]["passed"] = False
        self.result["trace"][1]["expect"]["log"] = [1, 2, 3, 4]
        text = render(self.result)
        self.assertNotIn("Step 3", text)
        self.assertIn("Callbacks during step = [2, 3, 4]", text)
        self.assertIn("Callbacks during step = [4]", text)
        self.assertIn("MISMATCH", text)

    def test_report_text_cannot_inject_mermaid_or_html(self):
        self.result["name"] = "</script>\n```\n%%{init:evil}%%"
        self.assertNotIn("script", render(self.result))
        self.result["trace"][0]["event"]["values"] = ["1; participant Evil"]
        with self.assertRaises(ValueError):
            render(self.result)

    def test_compact_or_empty_report_needs_trace(self):
        for result in [{"passed": True}, {"trace": []}]:
            with self.assertRaises(ValueError):
                render(result)
