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
- **Geography**: the mandatory-SAFMR metros across two states — Texas: Dallas,
  Fort Worth-Arlington, San Antonio (2018 cohort) and Beaumont-Port Arthur
  (2023 expansion); Kansas: Kansas City, MO-KS (KS side) and Wichita, KS (2023
  expansion) — 724 ZIP codes in all. Houston is **not** a mandatory-SAFMR metro
  (HUD publishes SAFMR data for it but does not mandate its use), so it is
  excluded; its adopted HCV standards live in
  `../payment_standards/zip_code_payment_standards.csv` instead. For the
  bi-state Kansas City metro only the KS-side ZIPs are bundled. Other areas keep
  the county FMR. ZIP codes that straddle two HUD Metro FMR Areas carry
  identical SAFMRs, so the table is unique per `(zip_code, year, bedrooms)`.

| column | type | meaning |
|---|---|---|
| `zip_code` | str | five-digit ZIP code |
| `hud_area_name` | str | HUD metro FMR area, suffixed with its 2-letter state (e.g. `Dallas, TX`, `Wichita, KS`); used for the SAFMR-for-HCV designation match |
| `year` | int | HUD fiscal year |
| `bedrooms` | int | 0 (efficiency) through 4 |
| `value` | float | monthly SAFMR in current-year dollars |

Source: HUD User FY2026 Small Area FMRs (revised),
<https://www.huduser.gov/portal/datasets/fmr/smallarea/index.html>.

### SAFMR-for-HCV applicability

Whether a SAFMR is the HCV payment standard for a ZIP is a policy question, not
a data-availability one. The policy primitive is HUD's list of metros where
SAFMR use is mandatory (2016 SAFMR Final Rule; 24 CFR §888.113), held as the
`SAFMR_HCV_DESIGNATED_METROS` constant in the `safmr_used_for_hcv` variable
(`Beaumont-Port Arthur, TX`, `Dallas, TX`, `Fort Worth, TX`, `San Antonio, TX`,
`Kansas City, KS`, `Wichita, KS` — matching the `hud_area_name` column here;
Houston is deliberately absent because it is not a mandatory-SAFMR metro).
`safmr_used_for_hcv` is true for a ZIP iff its
SAFMR row is in a designated metro, so the applicable ZIP set is just
`small_area_fair_market_rents` restricted to those metros — nothing to
duplicate or keep in sync.

This keeps the designation independent of the rent data: raw SAFMR data added
for other uses (e.g. a reform's rent cap) never makes those ZIPs adopt SAFMR as
their HCV payment standard. A PHA's published adopted schedule, where encoded in
`../payment_standards/zip_code_payment_standards.csv`, still takes precedence
over the SAFMR.

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
