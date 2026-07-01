# HUD Fair Market Rents (FMRs)

## What

`fair_market_rents.csv` holds HUD's published Fair Market Rents at the FMR-area
level, indexed by `(state, hud_fmr_area_code, year, bedrooms)`. FMRs are the
40th-percentile gross-rent estimates HUD uses to cap rents under the Housing
Choice Voucher program and size other federal housing subsidies (24 CFR Part
888).

The model variable `hud_fair_market_rent` reads from this CSV and normalizes
HUD FMR-area codes to PolicyEngine's five-digit `county_fips` input. When
several HUD FMR areas map to one county and no direct county row exists, the
loader uses the median FMR-area value as a lossy county-level fallback.

## Scope today

- **Years**: FY2025 and FY2026. `nearest_fmr_year` resolves each queried
  period to the matching fiscal year when its rows are present (period 2025 →
  FY2025, period 2026 → FY2026). Periods outside the bundled range fall back to
  the nearest bundled year (e.g. 2024 → FY2025, 2027 → FY2026).
- **Geography**: county-level lookup from HUD FMR areas (no SAFMR ZIP-level
  resolution here). Where HUD publishes one pseudo-area for a territory, that
  pseudo-area is expanded to the territory's county FIPS codes.
- **Connecticut**: HUD's FY2026 file adopts Connecticut's nine Census planning
  regions (FIPS `09110`–`09190`) in place of the eight legacy counties (FIPS
  `09001`–`09015`); Connecticut abolished county government in 1960 and the
  Census Bureau approved the planning regions as county-equivalents in 2022.
  PolicyEngine's `County` enum still uses the legacy counties. When a queried
  county/bedroom row is absent from the preferred fiscal year, such as legacy
  Connecticut counties in FY2026, `hud_fair_market_rent` falls back to the most
  recent earlier bundled year with a matching row rather than returning zero.
  **TODO**: this fallback depends on FY2025 remaining in the bundle. Migrate
  the `County` enum to Connecticut's planning regions (tracked in #8803)
  before FY2025 rows are ever dropped, or legacy CT counties will silently
  resolve to $0.
- **Data**: full FY2025 and FY2026 county-level HUD files.

## Schema

| column | type | meaning |
|---|---|---|
| `state` | str | two-letter state abbreviation |
| `hud_fmr_area_code` | str | HUD FMR-area code from the county-level source file |
| `year` | int | HUD fiscal year |
| `bedrooms` | int | 0 (efficiency) through 4 |
| `value` | float | monthly FMR in current-year dollars |

## Refresh

Two equivalent tools write this CSV; both **append** a new `--year` rather than
overwriting, so multiple fiscal years coexist.

From the HUD User API (needs a free `HUD_API_TOKEN`, register at
<https://www.huduser.gov/hudapi/>):

```
python -m policyengine_us.tools.download_hud_fmr --year 2025 --output \
    policyengine_us/parameters/gov/hud/fmr/fair_market_rents.csv
```

From HUD's published per-year Excel workbook (no token; needs `python-calamine`
— browse to Datasets > Fair Market Rents and download `FYXX_FMRs.xlsx`):

```
python -m policyengine_us.tools.convert_hud_fmr_xlsx --input FY26_FMRs.xlsx \
    --year 2026 --output \
    policyengine_us/parameters/gov/hud/fmr/fair_market_rents.csv
```

## Source

- HUD User FMR documentation: <https://www.huduser.gov/portal/datasets/fmr.html>
- FY2025 Federal Register notice: <https://www.federalregister.gov/documents/2024/08/14/2024-18002>
- FY2026 Federal Register notice: <https://www.federalregister.gov/documents/2025/08/22/2025-16060>
  (effective 2025-10-01).
- Regulatory citation: 24 CFR §888 (FMR rules), 24 CFR §982.503 (HCV payment
  standards bound to 90-110 percent of FMR).
