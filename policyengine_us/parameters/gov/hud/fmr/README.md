# HUD Fair Market Rents (FMRs)

## What

`fair_market_rents.csv` holds HUD's published Fair Market Rents at the FMR-area
level, indexed by `(state, hud_fmr_area_code, year, bedrooms)`. FMRs are the
40th-percentile gross-rent estimates HUD uses to cap rents under the Housing
Choice Voucher program, set Low-Income Housing Tax Credit rent limits, and
size other federal housing subsidies (24 CFR Part 888).

The model variable `hud_fair_market_rent` reads from this CSV and normalizes
HUD FMR-area codes to PolicyEngine's five-digit `county_fips` input. When
several HUD FMR areas map to one county and no direct county row exists, the
loader uses the median FMR-area value as a lossy county-level fallback.

## Scope today (Phase 1)

- **Year**: FY2025 only. The variable imputes unsupported years with the
  nearest bundled FMR year until more years are added.
- **Geography**: county-level lookup from HUD FMR areas. Where HUD publishes
  one pseudo-area for a territory, that pseudo-area is expanded to the
  territory's county FIPS codes. ZIP-level Small Area FMR resolution is now
  available for the in-scope metros via `small_area_fair_market_rents.csv`
  (see below).
- **Data**: full FY2025 county-level HUD file.

## Small Area FMRs (`small_area_fair_market_rents.csv`)

ZIP-level Small Area FMRs, indexed by `(zip_code, year, bedrooms)`, read by the
`small_area_fair_market_rent` variable. SAFMRs are 40th-percentile gross-rent
estimates computed per ZIP rather than per FMR area, and HUD mandates their use
for Housing Choice Voucher payment standards in designated metropolitan areas
(24 CFR §888.113).

- **Year**: FY2026 (HUD revised file). Unsupported years impute to the nearest
  bundled SAFMR year.
- **Geography**: the four Texas metros where SAFMR use is mandatory — Dallas,
  Fort Worth-Arlington, Houston, and San Antonio (834 ZIP codes). Other areas
  keep the county FMR. The handful of ZIP codes that straddle the Dallas and
  Fort Worth HUD Metro FMR Areas carry identical SAFMRs, so the table is unique
  per `(zip_code, year, bedrooms)`.

| column | type | meaning |
|---|---|---|
| `zip_code` | str | five-digit ZIP code |
| `hud_area_name` | str | HUD metro FMR area name (provenance only) |
| `year` | int | HUD fiscal year |
| `bedrooms` | int | 0 (efficiency) through 4 |
| `value` | float | monthly SAFMR in current-year dollars |

Source: HUD User FY2026 Small Area FMRs (revised),
<https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html>.

## Schema

| column | type | meaning |
|---|---|---|
| `state` | str | two-letter state abbreviation |
| `hud_fmr_area_code` | str | HUD FMR-area code from the county-level source file |
| `year` | int | HUD fiscal year |
| `bedrooms` | int | 0 (efficiency) through 4 |
| `value` | float | monthly FMR in current-year dollars |

## Refresh

```
python -m policyengine_us.tools.download_hud_fmr --year 2025 --output \
    policyengine_us/parameters/gov/hud/fmr/fair_market_rents.csv
```

The script reads `HUD_API_TOKEN` from the environment (register a free key
at <https://www.huduser.gov/hudapi/>). Re-running with a different `--year`
appends rather than overwriting.

## Source

- HUD User FY2025 FMR documentation: <https://www.huduser.gov/portal/datasets/fmr.html>
- Federal Register notice: <https://www.federalregister.gov/documents/2024/08/14/2024-18002>
- Regulatory citation: 24 CFR §888 (FMR rules), 24 CFR §982.503 (HCV payment
  standards bound to 90-110 percent of FMR).
