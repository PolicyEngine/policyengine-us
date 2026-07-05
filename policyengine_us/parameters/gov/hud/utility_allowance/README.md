# HUD utility allowances

County-level Housing Choice Voucher utility allowance schedules, used by
`hud_utility_allowance`.

Utility allowances are set per public housing agency (PHA) under
[24 CFR 982.517](https://www.law.cornell.edu/cfr/text/24/982.517), broken out by
dwelling-unit size (bedroom count) and utility/fuel type. HUD does not publish a
national dataset of these schedules, so `county_utility_allowances.csv` encodes
the schedules for the counties PolicyEngine currently models:

- **Los Angeles County, CA** (LACDA) — schedules effective 2023-07-01 (from
  LACDA's prior schedule PDF, no longer online; values match the table
  previously hardcoded in the model) and 2025-07-01.
- **Texas** — the 28 counties in the Texas Department of Housing and Community
  Affairs (TDHCA) Housing Choice Voucher service area, effective 2026-01-01.
- **Kansas** — Sedgwick (Wichita HA), Shawnee (Topeka HA), Wyandotte (Kansas
  City KS HA) and Johnson (Johnson County HA) counties.

## Convention

Each schedule is collapsed into a single monthly dollar amount per bedroom size
using one consistent convention, matching how LA County was originally modeled:

> **Multi-Family (apartment) unit type**, **all-electric** heating / cooking /
> water heating, and the **sum of every tenant-paid line item** — other electric,
> air conditioning, water, sewer, trash, the electric service charge, and the
> range and refrigerator appliance allowances.

Gas rows, gas service charges, and electric heat-pump rows are excluded. This is
an approximation: the model has a single `tenant_pays_utilities` flag and does
not know a household's actual fuel type or which specific utilities it pays.

## File format

`county_utility_allowances.csv` columns:

- `county_fips` — five-digit county FIPS code.
- `year` — the schedule's effective year. `hud_utility_allowance` uses the latest
  schedule at or before the simulated year (and the earliest schedule for years
  before it begins).
- `bedrooms` — bedroom count, or `-1` for single-room occupancy (SRO). Households
  larger than a schedule's top bedroom size reuse that top value. Counties whose
  PHA publishes no SRO row (all except LA County) receive a share of their
  zero-bedroom value (75% per
  [24 CFR 982.604(b)](https://www.law.cornell.edu/cfr/text/24/982.604)), set by
  the `sro_share_of_zero_bedroom` parameter and applied in the
  `hud_utility_allowance` formula.
- `monthly_value` — monthly utility allowance in dollars.

## Parameters

- `sro_share_of_zero_bedroom.yaml` — the SRO utility allowance as a share of the
  zero-bedroom allowance (0.75 per 24 CFR 982.604(b)). Applied post-lookup in the
  formula for counties whose PHA publishes no dedicated SRO row; a published SRO
  row (LA County) takes precedence and is not scaled.
