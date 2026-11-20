"""Safety regression tests for external listing publication. Run with unittest."""
import unittest
from unittest.mock import Mock
from auto_parts_publication import (
    PLATFORMS, ENABLED_CONNECTORS, validate_job, record_blocked, record_sale_closures, listing_status
)

class PublicationSafetyTests(unittest.TestCase):
    def test_no_unverified_connector_is_active(self):
        self.assertEqual(ENABLED_CONNECTORS, frozenset())
        for platform in PLATFORMS:
            with self.subTest(platform=platform), self.assertRaises(RuntimeError):
                validate_job(platform, "publish", 1000)

    def test_invalid_price_never_publishes(self):
        for price in (-1, 1.5, "100", None, True):
            with self.subTest(price=price), self.assertRaises(ValueError):
                validate_job("skelbiu_lt", "publish", price)

    def test_invalid_platform_or_action(self):
        for platform, action in (("unknown", "publish"), ("skelbiu_lt", "delete")):
            with self.assertRaises(ValueError):
                validate_job(platform, action, 100)

    def test_blocked_job_uses_parameterized_sql(self):
        conn = Mock()
        record_blocked(conn, "item-id", "skelbiu_lt", "publish", 2500)
        sql, params = conn.execute.call_args.args
        self.assertIn("ON CONFLICT", sql)
        self.assertEqual(params, ("item-id", "skelbiu_lt", "publish", 2500))
        self.assertNotIn("item-id", sql)

    def test_status_is_read_only_and_does_not_claim_blocked_jobs_succeeded(self):
        from datetime import datetime, timezone
        conn = Mock()
        now = datetime(2026, 11, 20, tzinfo=timezone.utc)
        conn.execute.return_value.fetchall.side_effect = [
            [("skelbiu_lt", "ext-1", "https://example.invalid/1", "active", 2500, None, now)],
            [("skelbiu_lt", "close", 2500, "blocked", 0,
              "No authorized verified connector", now)],
        ]
        state = listing_status(conn, "item-id")
        self.assertEqual(state["listings"][0]["status"], "active")
        self.assertEqual(state["jobs"][0]["status"], "blocked")
        self.assertEqual(state["connectors"]["facebook_marketplace"], "not_connected")
        self.assertEqual(conn.execute.call_count, 4)

    def test_sale_only_queues_existing_unclosed_listings(self):
        conn = Mock()
        conn.execute.return_value.fetchall.return_value = []
        self.assertEqual(record_sale_closures(conn, "item-id"), 0)
        self.assertEqual(conn.execute.call_count, 3)  # two CREATE TABLEs + SELECT

if __name__ == "__main__":
    unittest.main()
