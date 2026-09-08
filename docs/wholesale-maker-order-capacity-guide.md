# Wholesale Maker Order Capacity Planning Guide

Wholesale can increase revenue quickly, but a large order can also create a production bottleneck if materials, labor, lead times, and existing commitments are not checked together. A simple capacity planner helps a maker decide whether an order is realistic before promising a ship date.

## 1. Convert the order into production work

Start with the quantity required for each SKU and the realistic production rate.

`production hours = required units / units produced per hour`

If production happens in batches, calculate using whole batches instead of an idealized per-unit rate. Include setup, curing, cooling, drying, labeling, packing, or other time that limits throughput.

## 2. Separate labor time from elapsed lead time

Some products need little hands-on labor but many calendar days. A candle batch, for example, may need curing time after the active production work is complete.

Track both:

- hands-on production hours
- minimum elapsed production days

A promised wholesale date must satisfy both constraints.

## 3. Check materials before accepting the date

For every critical component, calculate:

`required material = units ordered × material per unit`

Then compare required material with usable stock. If replenishment is needed, add supplier lead time and a buffer for delays. Do not treat an order as production-ready just because the labor capacity exists.

For basic stock timing, the free [Reorder Point Calculator](https://tazeris-money-factory-production.up.railway.app/free/reorder-point-calculator?utm_source=github&utm_medium=owned&utm_campaign=wholesale_capacity_guide) can help with a simplified reorder estimate.

## 4. Reserve capacity for existing commitments

Available hours are not the same as total working hours. Subtract time already committed to:

- direct customer orders
- markets and events
- regular restocking
- administrative work
- planned days off
- maintenance or setup work

A useful simplified measure is:

`available production capacity = planned production hours - committed production hours`

Compare that number with the hours required by the new wholesale order.

## 5. Add a realistic safety buffer

Running at exactly 100% planned capacity leaves no room for defects, supplier delays, rework, illness, or slower-than-normal batches. Use a buffer appropriate for the business rather than promising the theoretical fastest date.

The goal is not to reject large orders. It is to quote a date that can actually be met.

## 6. Check order economics as well as capacity

A wholesale order that fills the schedule can crowd out higher-margin work. Before accepting, review:

- wholesale selling price
- unit cost
- packaging cost
- payment fees
- shipping responsibility
- total production hours
- expected contribution profit

Then compare the profit with the capacity consumed. High revenue alone does not guarantee that the order is a good use of limited production time.

## Reusable planning option

For a reusable worksheet that combines order size, production capacity, timing, and planning checks, see the current [Wholesale Maker Order Capacity Planner](https://tazeris-money-factory-production.up.railway.app/p/wholesale-maker-order-capacity-planner?utm_source=github&utm_medium=owned&utm_campaign=wholesale_capacity_guide).

The live product page contains the current description and purchase terms. This guide is educational planning information and does not replace accounting, legal, or financial advice.
