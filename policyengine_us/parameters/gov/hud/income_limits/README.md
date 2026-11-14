# HUD Section 8 Income Limits

`section8_income_limits.csv` contains HUD FY2017 through FY2026 Section 8
income limits from HUD's Income Limits datasets:

https://www.huduser.gov/portal/datasets/il.html

Each row is `(county_fips, year)` with the area median income (`ami`) and the
30% / 50% / 80% AMI limits at family sizes 1-8 (`extremely_low_income_N`,
`very_low_income_N`, `low_income_N`). The loader (`__init__.py`) selects, per
county, the latest bundled year less than or equal to the requested period, so
period 2024 uses FY2024, period 2025 uses FY2025, and period 2026 uses FY2026
(effective 2026-05-01); periods after the latest bundled year fall back to it.
Periods before FY2017 use the earliest bundled data; that fallback does not
establish the applicable limits in earlier years.

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
appends rather than overwrites. FY2017–22 name the geography column
`fips2010`; the converter accepts that legacy header as well as `fips`. The
optional refresh parser is pinned below and is not a model runtime dependency:

```
uv run --with python-calamine==0.9.1 \
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

## Historical time convention

The variables select the workbook's fiscal-year label for the entire modeled
YEAR. HUD's actual limits take effect during the year, on the dates below.
For example, period 2017 uses FY2017 values even before the source's April 14
effective date. This convention does not reconstruct the schedule legally in
force for a January 2017 applicant. Date-aware lookup and the preceding
FY2016 schedule require a separate change.

Historical income limits do not supply historical Fair Market Rents, adopted
PHA payment standards, utility allowances, HOTMA rules, or voucher availability.
They do not establish complete historical housing-assistance amounts.

## Historical source files

The original Section 8 workbooks below were retrieved from HUD on November 13,
2026. Their 24 published ELI/l50/l80 columns and median income feed the existing
county aggregation described above. FY2024–26 rows remain unchanged.

| FY | Effective date | Original workbook | SHA-256 |
| --- | --- | --- | --- |
| 2017 | 04/14/2017 | [Section8-FY17.xlsx](https://www.huduser.gov/portal/datasets/il/il17/Section8-FY17.xlsx) | `365e26f463e468b8fbf607e349dcaa3f02687b536dc8713d07fcc71411c6efc9` |
| 2018 | April 1, 2018 | [Section8-FY18.xlsx](https://www.huduser.gov/portal/datasets/il/il18/Section8-FY18.xlsx) | `4a16a2979d5047651c1992483b7bef9bc8758f2db5350d8013becc5a6a1c41f1` |
| 2019 | April 24, 2019 | [Section8-FY19.xlsx](https://www.huduser.gov/portal/datasets/il/il19/Section8-FY19.xlsx) | `b0b6228aa43fdb35726d71fa7961434f929ae7f5764783012552bdbf9e4d46d6` |
| 2020 | April 1, 2020 | [Section8-FY20.xlsx](https://www.huduser.gov/portal/datasets/il/il20/Section8-FY20.xlsx) | `9c64ea9648866bd244c3f218f2e2b17e80ffd13c25c3ccd4a01edbaaa600b51d` |
| 2021 | April 1, 2021 | [Section8-FY21.xlsx](https://www.huduser.gov/portal/datasets/il/il21/Section8-FY21.xlsx) | `ea83806a2a048126396ed3dc943c06b554e5d804e4fd860431455a8215322b2a` |
| 2022 | April 18, 2022 | [Section8-FY22.xlsx](https://www.huduser.gov/portal/datasets/il/il22/Section8-FY22.xlsx) | `c773765f96e7e5df65a43a1e0433f8c4f175491bb8ba52080fd7a78b9da4335e` |
| 2023 | May 15, 2023 | [Section8-FY23.xlsx](https://www.huduser.gov/portal/datasets/il/il23/Section8-FY23.xlsx) | `0f8ecdab7325cfa0fa132891d2e6a8caae9f27d6652cb101d4d12fe3dad21831` |
