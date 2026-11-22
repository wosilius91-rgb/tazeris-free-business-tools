"""Regression checks for inventory rules (no database or paid services)."""
import unittest
from datetime import datetime, timezone, timedelta
from auto_parts_domain import money, validate_valuation, public_visible, sales_report

class InventoryRulesTests(unittest.TestCase):
    def test_money_precision(self):
        self.assertEqual(money("12.34"), 1234)
        for value in ("-1", "NaN", "Infinity", "1000001"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                money(value)

    def test_valuation_requires_distinct_https_sources(self):
        sources = [
            {"url": "https://example.com/part/1", "price": "40"},
            {"url": "https://example.org/part/2", "price": "45"},
        ]
        self.assertEqual(validate_valuation("45", "35", sources), (4500, 3500))
        with self.assertRaises(ValueError):
            validate_valuation("30", "35", sources)
        with self.assertRaises(ValueError):
            validate_valuation("45", "35", [sources[0], sources[0]])
        with self.assertRaises(ValueError):
            validate_valuation("45", "35", [sources[0], {"url": "http://example.org/2", "price": "45"}])

    def test_sold_visibility_one_month(self):
        now = datetime(2026, 11, 22, tzinfo=timezone.utc)
        item = {"status": "sold", "sold_at": (now - timedelta(days=10)).isoformat()}
        self.assertTrue(public_visible(item, now))
        item["sold_at"] = datetime(2026, 9, 22, tzinfo=timezone.utc).isoformat()
        self.assertFalse(public_visible(item, now))

    def test_report_uses_actual_price(self):
        now = datetime(2026, 11, 22, tzinfo=timezone.utc)
        items = [{"status": "sold", "sold_at": now.isoformat(),
                  "actual_price_cents": 1234, "quick": 999}]
        report = sales_report(items, "7d", now)
        self.assertEqual(report["count"], 1)
        self.assertEqual(report["revenue_cents"], 1234)

if __name__ == "__main__":
    unittest.main()
