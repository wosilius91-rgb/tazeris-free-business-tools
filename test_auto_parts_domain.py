"""Regression tests for TAZERIS Auto Parts inventory rules (stdlib only).
Run: python -m unittest test_auto_parts_domain.py
"""
import unittest
from datetime import datetime, timezone, timedelta
from auto_parts_domain import money, month_ago, public_visible, sales_report, validate_valuation

NOW = datetime(2026, 11, 20, 12, 0, tzinfo=timezone.utc)

class InventoryRulesTests(unittest.TestCase):
    def test_money(self):
        self.assertEqual(money("12.50"), 1250)
        for value in ("-1", "NaN", "Infinity", "1000001"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                money(value)

    def test_public_visibility(self):
        self.assertTrue(public_visible({"status": "available"}, NOW))
        recent = (NOW - timedelta(days=5)).isoformat()
        old = (NOW - timedelta(days=50)).isoformat()
        self.assertTrue(public_visible({"status": "sold", "sold_at": recent}, NOW))
        self.assertFalse(public_visible({"status": "sold", "sold_at": old}, NOW))
        self.assertFalse(public_visible({"status": "draft"}, NOW))

    def test_month_end(self):
        self.assertEqual(month_ago(datetime(2026, 3, 31, tzinfo=timezone.utc), 1).day, 28)

    def test_report_periods(self):
        rows = [
            {"status": "sold", "sold_at": (NOW-timedelta(days=2)).isoformat(), "actual_price_cents": 1000},
            {"status": "sold", "sold_at": (NOW-timedelta(days=20)).isoformat(), "actual_price_cents": 2000},
            {"status": "available", "actual_price_cents": 9999},
        ]
        self.assertEqual(sales_report(rows, "7d", NOW)["revenue_cents"], 1000)
        self.assertEqual(sales_report(rows, "1m", NOW)["revenue_cents"], 3000)
        for period in ("3m", "6m", "12m"):
            self.assertEqual(sales_report(rows, period, NOW)["count"], 2)

    def test_valuation_evidence(self):
        sources = [{"url": "https://example.com/a"}, {"url": "https://example.org/b"}]
        self.assertEqual(validate_valuation(100, 85, sources), (10000, 8500))
        with self.assertRaises(ValueError):
            validate_valuation(100, 110, sources)
        with self.assertRaises(ValueError):
            validate_valuation(100, 85, sources[:1])

if __name__ == "__main__":
    unittest.main()
