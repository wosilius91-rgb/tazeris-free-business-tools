# Craft fair profit and restock: a worked example for handmade sellers

A busy stall is not necessarily a profitable stall. This guide shows a simple way to estimate what an event leaves after the costs you enter, then plan a reorder point. The examples are original TAZERIS calculator examples. You can use the free tools without buying anything.

**[Open the free Craft Fair Profit Calculator](https://tazeris-money-factory-production.up.railway.app/free/craft-fair-profit-calculator?utm_source=github&utm_medium=owned&utm_campaign=maker_guide)**

## 1. Separate sales from the costs of making those sales

Use one currency for every amount. For this example, a seller records:

| Input | Amount |
|---|---:|
| Sales collected | 600 |
| Cost of products sold | 180 |
| Booth fee | 80 |
| Travel | 35 |
| Other event costs | 20 |
| Payment fee rate | 2.5% |

The example assumes that the payment fee applies to all 600 of sales. Actual card and cash mixes can require a different effective rate. Include labor, packaging and other relevant costs consistently; avoid counting the same cost in two categories.

Payment fees = 600 × 0.025 = **15**.

Entered costs = 180 + 80 + 35 + 20 + 15 = **330**.

Sales minus entered costs = 600 − 330 = **270**.

Margin on sales = 270 ÷ 600 × 100 = **45%**.

The 270 is not automatically take-home profit. Taxes, labor, overhead, refunds or other costs not included in your inputs still need to be considered. The calculator cannot know what you left out.

## 2. Check product pricing before the next event

An overall event result does not tell you which individual products are worth restocking. Start with each product's material, labor and other relevant costs, then consider its selling price and fees.

**[Use the free Handmade Product Profit Calculator](https://tazeris-money-factory-production.up.railway.app/free/handmade-profit-calculator?utm_source=github&utm_medium=owned&utm_campaign=maker_guide)**

For Etsy sellers, the separate [Etsy fee and profit calculator](https://tazeris-money-factory-production.up.railway.app/free/etsy-fee-profit-calculator?utm_source=github&utm_medium=owned&utm_campaign=maker_guide) lets you explore the inputs shown in the tool. Check the fees applicable to your own seller account rather than assuming one fee schedule fits every country or transaction.

## 3. Estimate when to reorder

A simple planning rule is:

**Reorder point = average units used per day × supplier lead time in days + safety stock.**

For 3 units per day, a 10-day lead time and 10 units of safety stock:

3 × 10 + 10 = **40 units**.

This is a simplified planning estimate. Seasonality, demand spikes, outstanding orders and supplier delays can change the stock level you actually need. It is not an instruction to place an automatic purchase.

**[Open the free Reorder Point Calculator](https://tazeris-money-factory-production.up.railway.app/free/reorder-point-calculator?utm_source=github&utm_medium=owned&utm_campaign=maker_guide)**

## 4. Move from a one-off calculation to reusable records

The free calculators are intended for quick checks. For reusable spreadsheets, browse the existing [Handmade Seller Tools](https://tazeris-money-factory-production.up.railway.app/collections/handmade-seller-tools?utm_source=github&utm_medium=owned&utm_campaign=maker_guide). Options include event profit and reconciliation workbooks and a [Handmade Seller Profit & Inventory Bundle](https://tazeris-money-factory-production.up.railway.app/p/handmade-seller-profit-inventory-bundle?utm_source=github&utm_medium=owned&utm_campaign=maker_guide).

These workbook products are paid; the calculator examples are free. Read the product page for current price, included files, requirements and purchase terms. Purchases take place on TAZERIS, not GitHub. This guide is published by TAZERIS and is not an independent review or an Etsy endorsement.

## Run the small examples locally

The repository includes dependency-free Python examples:

```python
from calculators import craft_fair_profit, reorder_point

print(craft_fair_profit(600, 180, 80, 35, 20, 2.5))
# {'payment_fees': 15.0, 'costs': 330.0, 'profit': 270.0, 'margin_percent': 45.0}

print(reorder_point(3, 10, 10))
# 40
```

Run `python -m unittest discover -s tests -v` to check the included examples. No API key is needed.

For purchase questions, use [TAZERIS support](https://tazeris-money-factory-production.up.railway.app/support). Do not post customer details, private business records or payment information in public GitHub issues.
