"""Original TAZERIS planning examples. Same currency for all monetary inputs."""
import math


def _number(value):
    if isinstance(value, bool):
        raise ValueError("Enter a finite non-negative number")
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError("Enter a finite non-negative number")
    return value


def craft_fair_profit(sales, product_cost, booth_fee=0, travel=0,
                      other_costs=0, payment_fee_percent=0):
    sales, product_cost, booth_fee, travel, other_costs, rate = map(
        _number, (sales, product_cost, booth_fee, travel, other_costs,
                  payment_fee_percent))
    if rate >= 100:
        raise ValueError("Payment fee must be less than 100 percent")
    fees = sales * rate / 100
    costs = product_cost + booth_fee + travel + other_costs + fees
    profit = sales - costs
    return {"payment_fees": round(fees, 2), "costs": round(costs, 2),
            "profit": round(profit, 2),
            "margin_percent": round(profit / sales * 100, 2) if sales else None}


def reorder_point(daily_usage, lead_days, safety_stock=0):
    daily_usage, lead_days, safety_stock = map(
        _number, (daily_usage, lead_days, safety_stock))
    point = daily_usage * lead_days + safety_stock
    if not math.isfinite(point):
        raise ValueError("Inputs exceed supported calculation range")
    return math.ceil(point)
