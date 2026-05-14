# HUD Fair Market Rents (FMRs)

## What

`fair_market_rents.csv` holds HUD's published Fair Market Rents at the county
level, indexed by `(state, county_fips, year, bedrooms)`. FMRs are the
40th-percentile gross-rent estimates HUD uses to cap rents under the Housing
Choice Voucher program, set Low-Income Housing Tax Credit rent limits, and
size other federal housing subsidies (24 CFR Part 888).

The model variable `hud_fair_market_rent` reads from this CSV.

## Scope today (Phase 1)

- **Year**: FY2025 only.
- **Geography**: county-level FMR area only (no SAFMR ZIP-level resolution
  yet — that lands in Phase 1B).
- **Seed data**: a handful of placeholder rows (LA County) so the variable
  and tests have something to bind to. Run `tools/download_hud_fmr.py` to
  populate the full ~3,000-row county file from HUD's published data.

## Schema

| column | type | meaning |
|---|---|---|
| `state` | str | two-letter state abbreviation |
| `county_fips` | str | 5-digit county FIPS code (zero-padded) |
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
