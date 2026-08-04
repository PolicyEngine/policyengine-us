# HUD Section 8 Income Limits

`section8_income_limits.csv` contains HUD FY2024, FY2025, and FY2026 Section 8
income limits from HUD's Income Limits datasets:

https://www.huduser.gov/portal/datasets/il.html

Each row is `(county_fips, year)` with the area median income (`ami`) and the
30% / 50% / 80% AMI limits at family sizes 1-8 (`extremely_low_income_N`,
`very_low_income_N`, `low_income_N`). The loader (`__init__.py`) selects, per
county, the latest bundled year less than or equal to the requested period, so
period 2024 uses FY2024, period 2025 uses FY2025, and period 2026 uses FY2026
(effective 2026-05-01); periods after the latest bundled year fall back to it.

The `extremely_low_income_` / `very_low_income_` / `low_income_` values are
HUD's published `ELI_` / `l50_` / `l80_` columns taken verbatim — they already
reflect HUD's hold-harmless, high-cost, and national caps plus the
federal-poverty-guideline floor on the extremely-low-income tier — rather than
recomputed from the median.

The original HUD files include subcounty rows for some areas. PolicyEngine
currently stores county FIPS on households, so duplicate county-year rows are
collapsed to the median numeric value for that county-year. Direct county rows
therefore pass through unchanged, and subcounty-only counties use a lossy
county-level fallback, matching the Fair Market Rent lookup pattern.

Connecticut: from FY2025 onward HUD's Section 8 file uses Connecticut's nine
Census planning regions (FIPS `09110`-`09190`) in place of the eight legacy
counties (FIPS `09001`-`09015`) that FY2024 used, the same transition noted in
the FMR README. When a county row is absent from the latest bundled year the
loader carries forward that county's most recent earlier year, so legacy CT
counties still resolve via their FY2024 rows.

## Refresh

`tools/convert_hud_income_limits_xlsx.py` regenerates this CSV from HUD's
per-year Section 8 Income Limits workbook. huduser.gov serves the static
workbooks only to requests with a browser `User-Agent`; the FY2026 file is at
`https://www.huduser.gov/portal/datasets/il/il26/Section8-FY26.xlsx` (note the
directory is `il26`, not `il2026`). The converter merges into the existing CSV
(de-duplicates on `(county_fips, year)`), so re-running for a new `--year`
appends rather than overwrites:

```
python -m policyengine_us.tools.convert_hud_income_limits_xlsx \
    --input Section8-FY26.xlsx --year 2026 --output \
    policyengine_us/parameters/gov/hud/income_limits/section8_income_limits.csv
```

## Source

- HUD Income Limits documentation: <https://www.huduser.gov/portal/datasets/il.html>
- FY2026 Section 8 Income Limits workbook (effective 2026-05-01):
  <https://www.huduser.gov/portal/datasets/il/il26/Section8-FY26.xlsx>
  (retrieved 2026-07-06).
- FY2025 Section 8 Income Limits workbook:
  <https://www.huduser.gov/portal/datasets/il/il25/Section8-FY25.xlsx>.
- FY2024 Section 8 Income Limits workbook:
  <https://www.huduser.gov/portal/datasets/il/il24/Section8-FY24.xlsx>.
