# HUD Fair Market Rents (FMRs)

## What

`fair_market_rents.csv` holds HUD's published Fair Market Rents at the FMR-area
level, indexed by `(state, hud_fmr_area_code, year, bedrooms)`. The CSV retains HUD's published gross-rent amounts, including the historical
40th/50th-percentile schedules, without recomputing them from methodology
metadata. These references inform housing subsidy limits (24 CFR Part 888).

The model variable `hud_fair_market_rent` reads from this CSV and normalizes
HUD FMR-area codes to PolicyEngine's five-digit `county_fips` input. When
several HUD FMR areas map to one county and no direct county row exists, the
loader uses the median FMR-area value as a lossy county-level fallback.

## Scope today

- **Years**: FY2017 through FY2026. Each calendar-year model period selects
  the matching FY label, using that FY's latest revised annual snapshot.
  This convention does not reconstruct the initial October schedule or later
  within-FY revisions. It does not certify January law. Before the bundle,
  2016 falls back to FY2017; after it, 2027 falls back to FY2026.
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
- **Data**: the eight revised FY2017–FY2024 workbooks add 38,130 source-area
  rows, or 190,650 bedroom values. All 47,640 existing FY2025–FY2026 physical
  CSV rows remain byte-identical. The CSV contains 238,290 rows in total.
- **Retired geography**: the existing prior-row lookup now finds historical
  values for four county FIPS absent from the original FY2025–FY2026 bundle:
  `02261` (last FY2022), `02270` and `46113` (FY2017), and `51515` (FY2019).
  Requests for those retired codes can therefore change in current years.
  Physical-row preservation is not a guarantee for every raw-FIPS request.
- **Limits**: this county-FMR data does not add historical SAFMR designation,
  PHA adopted payment standards, utility allowances, voucher availability,
  or complete historical housing-assistance payments.

## Historical source vintages

HUD's [original index](https://www.huduser.gov/portal/datasets/fmr.html)
links each initial schedule and revised workbook below. The revision date
applies to changed areas; unchanged rows retain the initial schedule. FY2024's
revision concerns Urban Honolulu. FY2017 also corrects four subcounty area
identifiers within the same counties. Retain the latest revised file for each
FY when refreshing this annual bundle; exclude hypothetical, ERAP, unadjusted
flat-rent, and Small Area FMR files.

| FY | Initial schedule and date | Selected revised workbook and listed revision date |
|---|---|---|
| 2017 | [FY2017_4050_FMR.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2017/FY2017_4050_FMR.xlsx), 2016-10-01 | [FY2017-4050-County-Level_Data.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2017/FY2017-4050-County-Level_Data.xlsx), 2017-05-01 |
| 2018 | [FY18_4050_FMRs.xls](https://www.huduser.gov/portal/datasets/fmr/fmr2018/FY18_4050_FMRs.xls), 2017-10-02 | [FY18_4050_FMRs_rev.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2018/FY18_4050_FMRs_rev.xlsx), 2018-03-22 |
| 2019 | [FY19_4050_FMRs.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2019/FY19_4050_FMRs.xlsx), 2018-10-01 | [FY2019_4050_FMRs_rev2.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2019/FY2019_4050_FMRs_rev2.xlsx), 2019-04-15 |
| 2020 | [FY20_4050_FMRs.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2020/FY20_4050_FMRs.xlsx), 2019-10-01 | [FY20_4050_FMRs_rev.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2020/FY20_4050_FMRs_rev.xlsx), 2020-04-10 |
| 2021 | [FY21_FMRs_cbo.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2021/FY21_FMRs_cbo.xlsx), 2020-10-01 | [FY21_4050_FMRs_rev.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2021/FY21_4050_FMRs_rev.xlsx), 2021-04-01 |
| 2022 | [FY22_FMRs.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2022/FY22_FMRs.xlsx), 2021-10-01 | [FY22_FMRs_revised.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2022/FY22_FMRs_revised.xlsx), 2022-04-09 |
| 2023 | [FY23_FMRs.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2023/FY23_FMRs.xlsx), 2022-10-01 | [FY23_FMRs_revised.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2023/FY23_FMRs_revised.xlsx), 2023-04-19 |
| 2024 | [FY24_FMRs.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2024/FY24_FMRs.xlsx), 2023-10-01 | [FMR2024_final_revised.xlsx](https://www.huduser.gov/portal/datasets/fmr/fmr2024/FMR2024_final_revised.xlsx), 2024-03-11 |

SHA-256 of the selected original workbooks:

| FY | SHA-256 |
|---|---|
| 2017 | `25eca87e4895d502299e99e5c0355e1505b59067d8676ea157e59e84b2e42f9e` |
| 2018 | `868c481f2f0522a30653a32c2ce3f42d5a6281c7e1c948a82da9d929f2eed0ce` |
| 2019 | `1a49879cd90d4c95fbeb11e1705fc5942d05fd2ad9ed5a33b06b8360118b653c` |
| 2020 | `5e833200b10aed43cf04dc0ed177e95099a7e52746cc9996613c4cc9bf25c711` |
| 2021 | `126bf6c05e26aec875b894e2ab24df3b3687fe65a90143f0b5dd518731ffd558` |
| 2022 | `e9724ee10a83e9a29fce9bebd76ff8e75152becc82b1e0193ab3af44a8ba7479` |
| 2023 | `91e2fbb54228f45c5045f35dec5414664ccfe9021817c1021c6e186d1595cf9e` |
| 2024 | `0a6634d5745e07f0638efe2aca65161b4b8d6982ebd4d257e8191ed18ecfbf98` |

All five published bedroom columns and every source-area identifier are retained.
The converter normalizes numeric identifiers; the loader restores their county
prefix with ten-digit padding where necessary. FY2017 uses `fmr0` through
`fmr4`, `fips2010`, and `state_alpha`; later aliases include `fmr_0` through
`fmr_4`, `fips`, and `stusps`. County aggregation and territory expansion follow
the existing loader described above.

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
<https://www.huduser.gov/portal/dataset/fmr-api.html>):

```
python -m policyengine_us.tools.download_hud_fmr --year 2025 --output \
    policyengine_us/parameters/gov/hud/fmr/fair_market_rents.csv
```

From HUD's published per-year Excel workbook (no token; the optional refresh
parser is pinned here and is not a runtime dependency):

```
uv run --with python-calamine==0.9.1 \
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
