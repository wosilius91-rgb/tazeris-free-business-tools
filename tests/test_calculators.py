import unittest
from calculators import craft_fair_profit, reorder_point


class CalculatorsTest(unittest.TestCase):
    def test_event_example(self):
        result = craft_fair_profit(600, 180, 80, 35, 20, 2.5)
        self.assertEqual(result["profit"], 270)
        self.assertEqual(result["payment_fees"], 15)
        self.assertEqual(result["margin_percent"], 45)

    def test_zero_sales(self):
        result = craft_fair_profit(0, 0, 50)
        self.assertEqual(result["profit"], -50)
        self.assertIsNone(result["margin_percent"])

    def test_reorder_example(self):
        self.assertEqual(reorder_point(3, 10, 10), 40)
        self.assertEqual(reorder_point(0.25, 3, 0), 1)

    def test_invalid_values(self):
        for value in (-1, float("nan"), float("inf"), True):
            with self.assertRaises(ValueError):
                reorder_point(value, 10)
        with self.assertRaises(ValueError):
            craft_fair_profit(100, 20, payment_fee_percent=100)


if __name__ == "__main__":
    unittest.main()
