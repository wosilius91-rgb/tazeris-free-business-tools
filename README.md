# TAZERIS free business calculators

Free browser tools and small, dependency-free Python examples for makers and small sellers. You can use the free tools without buying a workbook.

## Use a calculator in your browser

- [Handmade Product Profit Calculator](https://tazeris-money-factory-production.up.railway.app/free/handmade-profit-calculator?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [Craft Fair Profit Calculator](https://tazeris-money-factory-production.up.railway.app/free/craft-fair-profit-calculator?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [Reorder Point Calculator](https://tazeris-money-factory-production.up.railway.app/free/reorder-point-calculator?utm_source=github&utm_medium=owned&utm_campaign=free_tools)

## Worked examples

At a craft fair, sales of 600, product costs of 180, a booth fee of 80, travel of 35, other costs of 20 and payment fees of 2.5% leave 270 before any costs or taxes not entered. Use the same currency for every input.

For stock used at 3 units per day, a 10-day supplier lead time and 10 units of safety stock, the reorder point is 40 units. This is a simplified planning rule, not an automatic purchase instruction.

```python
from calculators import craft_fair_profit, reorder_point
print(craft_fair_profit(600, 180, 80, 35, 20, 2.5))
print(reorder_point(3, 10, 10))
```

Run the included checks with `python -m unittest discover -s tests -v`. The Python examples run locally, make no network requests and require no API key.

## Optional paid workbooks

The calculators are free. For reusable spreadsheet files, compare the current [TAZERIS seller tools](https://tazeris-money-factory-production.up.railway.app/collections/handmade-seller-tools?utm_source=github&utm_medium=owned&utm_campaign=free_tools). Descriptions, current prices and purchase terms are on the product pages.

- [Handmade Seller Profit & Inventory Bundle](https://tazeris-money-factory-production.up.railway.app/p/handmade-seller-profit-inventory-bundle?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [Craft Market Booth Profit and Reconciliation Spreadsheet](https://tazeris-money-factory-production.up.railway.app/p/craft-market-booth-profit-reconciliation-spreadsheet?utm_source=github&utm_medium=owned&utm_campaign=free_tools)

Purchases are made on the TAZERIS storefront, not on GitHub. The free examples do not include the paid workbook files.

## Scope and support

These are planning estimates, not accounting, tax or financial advice. Demand, fees, supplier lead times and omitted costs can change the result.

For product questions or purchase help, use [TAZERIS support](https://tazeris-money-factory-production.up.railway.app/support). Do not post payment details, customer information or private business records in public issues.

## License

The original Python examples in this repository use the MIT license. Paid workbooks have their own purchase terms; they are not included in this license.
