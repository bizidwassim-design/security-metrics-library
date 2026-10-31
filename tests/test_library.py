#!/usr/bin/env python3
"""Tests for the Security Metrics & KPI Library (run: python -m unittest discover -s tests)."""
from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_catalogue  # noqa: E402
import trend_report  # noqa: E402


class LibraryValidation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.metrics = build_catalogue.load_metrics()

    def test_library_is_valid(self):
        self.assertEqual(build_catalogue.validate(self.metrics), [])

    def test_minimum_size_and_categories(self):
        self.assertGreaterEqual(len(self.metrics), 40)
        cats = {m["category"] for m in self.metrics}
        self.assertEqual(cats, set(build_catalogue.CATEGORIES), "every category must have at least one metric")

    def test_ids_follow_category_prefix(self):
        prefix = {"governance": "GOV", "identity": "IDN", "vulnerability": "VUL", "endpoint": "END",
                  "detection-response": "DR", "awareness": "AWR", "third-party": "TPR", "cloud": "CLD", "ai": "AI"}
        for m in self.metrics:
            self.assertTrue(m["id"].startswith(prefix[m["category"]] + "-"), m["id"])

    def test_board_pack_has_ten_ranked_metrics(self):
        ranks = sorted(m["board"]["rank"] for m in self.metrics if m.get("board"))
        self.assertEqual(ranks, list(range(1, 11)))

    def test_validator_catches_problems(self):
        broken = [dict(m) for m in self.metrics]
        broken[0] = dict(broken[0], id=broken[1]["id"], category="nonsense")
        problems = build_catalogue.validate(broken)
        self.assertTrue(any("duplicate id" in p for p in problems))
        self.assertTrue(any("category" in p for p in problems))

    def test_every_metric_has_target_and_pitfall(self):
        for m in self.metrics:
            self.assertIsInstance(m["target_value"], (int, float), m["id"])
            self.assertGreaterEqual(len(m["pitfalls"]), 1, m["id"])


class GeneratedFilesAreCurrent(unittest.TestCase):
    """The committed generated files must match what the scripts produce now."""

    def test_catalogue_and_board_pack(self):
        metrics = build_catalogue.load_metrics()
        expected = "\n".join(build_catalogue.render_catalogue(metrics)).rstrip("\n") + "\n"
        self.assertEqual((ROOT / "docs" / "catalogue.md").read_text(encoding="utf-8"), expected)
        expected = "\n".join(build_catalogue.render_board_pack(metrics)).rstrip("\n") + "\n"
        self.assertEqual((ROOT / "docs" / "board-pack.md").read_text(encoding="utf-8"), expected)

    def test_csv_matches_yaml(self):
        metrics = build_catalogue.load_metrics()
        with (ROOT / "data" / "metrics.csv").open(encoding="utf-8", newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual([r["id"] for r in rows], [m["id"] for m in metrics])
        self.assertEqual(rows[0].keys().__len__(), len(build_catalogue.CSV_COLUMNS))

    def test_trend_report_matches_sample(self):
        meta = trend_report.load_metadata(trend_report.DEFAULT_YAML)
        series = trend_report.load_values(trend_report.DEFAULT_VALUES)
        expected = "\n".join(trend_report.render(series, meta, "sample-values.csv")).rstrip("\n") + "\n"
        self.assertEqual((ROOT / "examples" / "trend-report.md").read_text(encoding="utf-8"), expected)


class TrendReportLogic(unittest.TestCase):
    def test_sparkline_shape(self):
        self.assertEqual(trend_report.sparkline([1, 2, 3, 4, 5, 6, 7, 8]), "▁▂▃▄▅▆▇█")
        self.assertEqual(trend_report.sparkline([5, 5, 5]), "▄▄▄")
        self.assertEqual(trend_report.sparkline([]), "")

    def test_status_by_direction(self):
        self.assertEqual(trend_report.status(99.1, 99, "higher"), "On target")
        self.assertEqual(trend_report.status(5.1, 5, "lower"), "Near target")
        self.assertEqual(trend_report.status(60, 99, "higher"), "Off target")
        self.assertEqual(trend_report.status(3.6, 4, "lower"), "On target")

    def test_trend_direction(self):
        self.assertEqual(trend_report.trend([10, 10, 10, 20, 20, 20], "higher"), "Improving")
        self.assertEqual(trend_report.trend([10, 10, 10, 20, 20, 20], "lower"), "Worsening")
        self.assertEqual(trend_report.trend([10, 10, 10, 10, 10, 10], "higher"), "Flat")
        self.assertEqual(trend_report.trend([1, 2], "higher"), "n/a")

    def test_sample_values_cover_twelve_months_for_eight_metrics(self):
        series = trend_report.load_values(trend_report.DEFAULT_VALUES)
        self.assertEqual(len(series), 8)
        for mid, points in series.items():
            self.assertEqual(len(points), 12, mid)

    def test_cli_writes_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.md"
            rc = trend_report.main(["--out", str(out)])
            self.assertEqual(rc, 0)
            self.assertIn("# Security metrics trend report", out.read_text(encoding="utf-8"))

    def test_unknown_metric_is_rejected(self):
        meta = trend_report.load_metadata(trend_report.DEFAULT_YAML)
        with self.assertRaises(KeyError):
            trend_report.render({"XXX-99": [("2026-01", 1.0)]}, meta, "x.csv")


if __name__ == "__main__":
    unittest.main()
