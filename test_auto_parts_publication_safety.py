"""Safety regression tests for the outbound listing guardrails.

Run: python -m unittest test_auto_parts_publication_safety.py
No external accounts, network calls or database needed.
"""
import unittest
import auto_parts_publication as publication


class PublicationSafetyTests(unittest.TestCase):
    def test_unverified_connectors_are_disabled(self):
        self.assertEqual(publication.ENABLED_CONNECTORS, frozenset())
        for platform in publication.PLATFORMS:
            with self.assertRaises(RuntimeError):
                publication.validate_job(platform, "publish", 1500)
            with self.assertRaises(RuntimeError):
                publication.validate_job(platform, "update", 1500)
            with self.assertRaises(RuntimeError):
                publication.validate_job(platform, "close", 0)

    def test_price_validation(self):
        for invalid in (None, -1, 0, 12.5, "1200", True):
            for action in ("publish", "update"):
                with self.subTest(invalid=invalid, action=action):
                    with self.assertRaises(ValueError):
                        publication.validate_job("skelbiu_lt", action, invalid)

    def test_unknown_platform_and_action_rejected(self):
        with self.assertRaises(ValueError):
            publication.validate_job("unknown", "publish", 1000)
        with self.assertRaises(ValueError):
            publication.validate_job("skelbiu_lt", "delete", 1000)


if __name__ == "__main__":
    unittest.main()
