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

---

# Small Area Fair Market Rents (SAFMRs)

## What

`small_area_fair_market_rents.csv` holds HUD's ZIP-code-level Small Area FMRs,
indexed by `(zip_code, year, bedrooms)`. SAFMRs replace a single metro-wide FMR
with a per-ZIP 40th-percentile rent so Housing Choice Voucher payment standards
track neighborhood rents. HUD mandates SAFMR use for HCV payment standards in
designated metros (24 CFR §888.113; HUD's designated-SAFMR-areas list).

The model variable `small_area_fair_market_rent` reads this CSV, and
`safmr_used_for_hcv` gates whether a ZIP's SAFMR is the household's HCV payment
standard basis (only inside the mandatory-SAFMR metros bundled here).

## Scope today

- **Years**: FY2025 and FY2026. `nearest_safmr_year` resolves each queried
  period to the matching fiscal year when its rows are present (period 2025 →
  FY2025, period 2026 → FY2026). Periods outside the bundled range fall back to
  the nearest bundled year (2024 → FY2025, 2027 → FY2026).
- **Geography**: the six metros where HUD mandates SAFMRs and PolicyEngine has
  ZIP coverage — Dallas, Fort Worth-Arlington, San Antonio-New Braunfels, and
  Beaumont-Port Arthur (TX) plus Kansas City (KS side) and Wichita (KS). All
  six appear on HUD's FY2025 designated-SAFMR-areas list with implementation
  dates of 1/1/2025 or earlier, so their SAFMRs are the HCV basis for both
  bundled years. The `hud_area_name` column is a curated metro label, not HUD's
  raw FMR-area name; the ZIP set is the union HUD publishes across these metros.
- **Data**: 724 ZIPs for FY2026 and 722 ZIPs for FY2025. Two ZIPs (`75429`
  Dallas, `78284` San Antonio) exist only in the FY2026 SAFMR file — HUD did
  not publish FY2025 SAFMRs for them, so they have no FY2025 rows and resolve
  to the county FMR at period 2025 rather than a fabricated value. Each ZIP
  carries 0-4 bedrooms; larger units add 15% of the 4-bedroom value per extra
  bedroom in the variable.

## Schema

| column | type | meaning |
|---|---|---|
| `zip_code` | str | five-digit ZIP code |
| `hud_area_name` | str | curated metro label (e.g. `Dallas, TX`) |
| `year` | int | HUD fiscal year |
| `bedrooms` | int | 0 (efficiency) through 4 |
| `value` | float | monthly SAFMR (the raw `SAFMR XBR` column, not a 90/110% payment-standard limit) in current-year dollars |

## Refresh

SAFMRs are extracted from HUD's published per-year SAFMR Excel workbook (browse
to Datasets > Fair Market Rents > Small Area FMRs). The workbook's raw
`SAFMR 0BR`…`SAFMR 4BR` columns become the `value` column; the 90%/110%
payment-standard columns are ignored. Reuse the bundled ZIP set and metro labels
and merge on `(zip_code, year, bedrooms)` so fiscal years coexist. `convert_hud_fmr_xlsx.py`
handles the county-FMR workbook only, not the SAFMR workbook.

## Source

- HUD SAFMR data portal: <https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html>
- FY2025 SAFMR workbook: <https://www.huduser.gov/portal/datasets/fmr/fmr2025/fy2025_safmrs.xlsx>
  (retrieved 2026-07-06).
- FY2026 SAFMR workbook: <https://www.huduser.gov/portal/datasets/fmr/fmr2026/fy2026_safmrs.xlsx>
  (retrieved 2026-07-06).
- FY2025 designated-SAFMR-areas list (mandatory metros, implementation dates):
  <https://www.huduser.gov/portal/datasets/fmr/fmr2025/designated-safmr-areas.pdf>
  (retrieved 2026-07-06).
- Regulatory citation: 24 CFR §888.113 (mandatory SAFMR metros), 24 CFR
  §982.503 (HCV payment standards, 90-110 percent of the applicable FMR).
