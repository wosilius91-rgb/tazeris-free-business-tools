# TAZERIS free business calculators

Free browser tools and small, dependency-free Python examples for makers and small sellers. You can use the free tools without buying a workbook.

## Use a calculator in your browser

- [Handmade Product Profit Calculator](https://tazeris-money-factory-production.up.railway.app/free/handmade-profit-calculator?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [Craft Fair Profit Calculator](https://tazeris-money-factory-production.up.railway.app/free/craft-fair-profit-calculator?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [Reorder Point Calculator](https://tazeris-money-factory-production.up.railway.app/free/reorder-point-calculator?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [Etsy Fee, Profit & Target Price Calculator](https://tazeris-money-factory-production.up.railway.app/free/etsy-fee-profit-calculator?utm_source=github&utm_medium=owned&utm_campaign=free_tools)

## Practical seller guides

These short guides cover common search and planning tasks for makers and Etsy sellers. The live versions connect directly to the relevant free calculator and reusable tools; the Markdown source remains public in this repository.

- [Etsy Pricing Calculator 2026: Price for Real Profit](https://tazeris-money-factory-production.up.railway.app/guides/etsy-pricing-calculator-2026?utm_source=github&utm_medium=owned&utm_campaign=seller_guides) — [Markdown source](docs/etsy-pricing-calculator-2026-guide.md)
- [Handmade Inventory & Reorder Tracker for Small Makers](https://tazeris-money-factory-production.up.railway.app/guides/handmade-inventory-reorder-tracker?utm_source=github&utm_medium=owned&utm_campaign=seller_guides) — [Markdown source](docs/handmade-inventory-reorder-tracker-guide.md)
- [Craft Fair Booth Profit Planner for Handmade Sellers](https://tazeris-money-factory-production.up.railway.app/guides/craft-fair-booth-profit-planner?utm_source=github&utm_medium=owned&utm_campaign=seller_guides) — [Markdown source](docs/craft-fair-booth-profit-planner-guide.md)
- [Maker Market Sales, Inventory & Pricing Guide](docs/maker-market-sales-inventory-pricing-guide.md)
- [True Margin Monitoring for Small Product Businesses](docs/true-margin-monitor-guide.md)
- [Wholesale Maker Order Capacity Planning Guide](docs/wholesale-maker-order-capacity-guide.md)
- [Craft Fair Profit and Restock Guide](docs/craft-fair-profit-and-restock-guide.md)

## Browse seller tools

- [Handmade Seller Tools](https://tazeris-money-factory-production.up.railway.app/collections/handmade-seller-tools?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [Etsy Seller Pricing, Profit & Inventory Tools](https://tazeris-money-factory-production.up.railway.app/collections/etsy-seller-tools?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [About TAZERIS & how purchases work](https://tazeris-money-factory-production.up.railway.app/about?utm_source=github&utm_medium=owned&utm_campaign=free_tools)

## New TAZERIS tools

The Money Factory keeps testing and publishing new small-business tools. These are recent live additions from the current catalog:

- [Maker Market Sales, Inventory & Pricing Spreadsheet](https://tazeris-money-factory-production.up.railway.app/p/maker-market-sales-inventory-pricing-spreadsheet?utm_source=github&utm_medium=owned&utm_campaign=new_tools)
- [True Margin Monitor](https://tazeris-money-factory-production.up.railway.app/p/true-margin-monitor?utm_source=github&utm_medium=owned&utm_campaign=new_tools)
- [Wholesale Maker Order Capacity Planner](https://tazeris-money-factory-production.up.railway.app/p/wholesale-maker-order-capacity-planner?utm_source=github&utm_medium=owned&utm_campaign=new_tools)

## TAZERIS fixed-scope digital services

These public service pages explain the starting scope and price before the secure order flow. Standard fixed-scope orders can be started online without a sales call.

- [Website repair from €49](https://tazeris-money-factory-production.up.railway.app/services/website-fix?utm_source=github&utm_medium=owned&utm_campaign=factory_services)
- [Telegram bot MVP from €79](https://tazeris-money-factory-production.up.railway.app/services/telegram-bot?utm_source=github&utm_medium=owned&utm_campaign=factory_services)
- [Android app MVP from €149](https://tazeris-money-factory-production.up.railway.app/services/android-mvp?utm_source=github&utm_medium=owned&utm_campaign=factory_services)

Only the fixed scope shown on the linked order page is included at the stated starting price. Do not put passwords, card details or other secrets into public project descriptions.

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

The calculators are free. For reusable spreadsheet files, compare the current [Handmade seller tools](https://tazeris-money-factory-production.up.railway.app/collections/handmade-seller-tools?utm_source=github&utm_medium=owned&utm_campaign=free_tools) or [Etsy seller tools](https://tazeris-money-factory-production.up.railway.app/collections/etsy-seller-tools?utm_source=github&utm_medium=owned&utm_campaign=free_tools). Descriptions, current prices and purchase terms are on the product pages.

- [Handmade Seller Profit & Inventory Bundle](https://tazeris-money-factory-production.up.railway.app/p/handmade-seller-profit-inventory-bundle?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [Craft Market Booth Profit and Reconciliation Spreadsheet](https://tazeris-money-factory-production.up.railway.app/p/craft-market-booth-profit-reconciliation-spreadsheet?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [Etsy Handmade Product Pricing and Profit Spreadsheet](https://tazeris-money-factory-production.up.railway.app/p/etsy-handmade-product-pricing-profit-spreadsheet?utm_source=github&utm_medium=owned&utm_campaign=free_tools)
- [Etsy Seller True-Profit and Reorder Spreadsheet](https://tazeris-money-factory-production.up.railway.app/p/etsy-seller-true-profit-reorder-spreadsheet?utm_source=github&utm_medium=owned&utm_campaign=free_tools)

Purchases are made on the TAZERIS storefront, not on GitHub. The free examples do not include the paid workbook files.

## Scope and support

These are planning estimates, not accounting, tax or financial advice. Demand, fees, supplier lead times and omitted costs can change the result.

For product questions or purchase help, use [TAZERIS support](https://tazeris-money-factory-production.up.railway.app/support). Do not post payment details, customer information or private business records in public issues.

## License

The original Python examples in this repository use the MIT license. Paid workbooks have their own purchase terms; they are not included in this license.
