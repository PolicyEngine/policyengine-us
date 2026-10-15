# Locality sales tax rates: sources and terms

`rates.csv` and `populations.csv` are built by
`scripts/local_sales_tax_rates/build.py` from official state files only. Where
PolicyEngine has no official locality rates, it applies no local rate: the
combined rate defaults to the state rate in the IRS state table heading, and
users can enter their own combined or local rate.

**Coverage regression against main.** The 16 states with local general sales
taxes but no official rate file in this build are AL, AK, AZ, CA, CO, FL,
HI, ID, IL, LA, MO, MS, NM, PA, SC and TX. Without a user-entered combined
or local rate, their modeled local amount is now $0; main approximated it
as 20% of the state table amount. This represents missing locality data,
not an assertion that those localities impose no sales tax. For example,
a Houston single filer with $85,000 of wages in 2025 has a state table
amount of $849: main's local amount was $849 × 0.20 = $169.80, and this
build's default is $0. At Houston's 8.25% combined rate, the worksheet gives
$849 × (8.25 − 6.25) / 6.25 = $271.68.

The household example does not establish aggregate deduction or tax
impacts, which also depend on the income-tax election, itemization and the
SALT limit. Houston's combined rate is documented in its
[FY2025 adopted budget, Sales Tax (PDF p. 8)](https://www.houstontx.gov/budget/25budadopt/II_GFR.pdf#page=8).

Official follow-up sources consistent with the official-files requirement
include Florida DOR's [DR-15DSS county discretionary sales surtax table](https://floridarevenue.com/Forms_library/current/dr15dss.pdf)
and the California CDTFA [city and county sales and use tax rates and downloadable rate files](https://www.cdtfa.ca.gov/taxes-and-fees/sales-use-tax-rates.htm).

`rates.csv` holds the combined state and local general sales tax rate
(general intrastate rate) of each county's places with their own rate and of
the county's area outside them, from 2022, and `populations.csv` the 2020
Census population of each. `place_counties.csv` maps every Census place in
the covered states to its principal county, including places pruned from
the rate file, and includes single-county places elsewhere.
`state_rates.csv` holds each covered state's
general sales tax rate (worksheet line 3 is the combined rate less it),
except Nevada's: its files fold the state rate into county rates, and the
IRS has Nevada residents enter the combined rate above the 6.85% heading. They carry only rates and Census codes derived from the sources below,
not the sources' files.

Retrieved 2026-10-06 (from 11:00 UTC). `scripts/local_sales_tax_rates/manifest.json` lists the
SHA-256 of every input file and the build log.

Vermont's coded municipal units are also checked against the Department of
Taxes' [Local Option Tax list](https://tax.vermont.gov/business/local-option-tax),
including effective dates and Montgomery's October 2025 rescission. The
short factual transcription is `scripts/local_sales_tax_rates/vt_local_option.csv`
(checked October 14, 2026); it distinguishes Rutland City (July 2023) from
Rutland Town (April 2009). Essex Junction uses its 2020 Census place code;
the other entries use county-subdivision codes.
The cross-check logs every difference and rejects any over one basis point;
the existing record-weighted method puts Barre City at 6.9976841% in the
October 2022 snapshot, within that tolerance of its statutory 7%.

## Rates

| States | Source | Files | Terms |
|---|---|---|---|
| Arkansas, Georgia, Iowa, Kansas, Minnesota, Nebraska, Nevada, North Carolina, North Dakota, Ohio, Oklahoma, South Dakota, Tennessee, Utah, Vermont, Washington, West Virginia, Wisconsin, Wyoming | Each state's rate and boundary files, posted on the Streamlined Sales Tax Governing Board website under the Streamlined Sales and Use Tax Agreement (SSUTA) sections 305 to 307 ([rate and boundary files](https://www.streamlinedsalestax.org/Shared-Pages/rate-and-boundary-files); format in the SST Technology Guide, chapter 5) | The latest rate file (`ratesandboundry/Rates/`) and boundary file (`ratesandboundry/Boundary/`) each state had posted on 2026-10-06, named in `manifest.json` (for example `WAR2026Q4AUG27.zip` and `WAB2026Q4AUG27.zip`). Each file keeps its rows' effective begin and end dates, which give the rates back to 2022. | No licence is attached to the files. The SST Technology Guide (May 2022) summarizes SSUTA section 307: "Database must be provided at no cost to the user of the database." The website carries "© Copyright 2018 Streamlined Sales Tax Governing Board, Inc." for the site. The rates are facts set by state and local law. |
| Indiana, Kentucky, Michigan, New Jersey, Rhode Island | The same SST files | | These states have no local general sales tax; the IRS has their residents enter no local sales tax, so the files are not used. |
| New York | New York State Department of Taxation and Finance, [Publication 718](https://www.tax.ny.gov/pdf/publications/sales/pub718.pdf) (2/25), "New York State Sales and Use Tax Rates by Jurisdiction, Effective March 1, 2025", for the combined rate of each county and city; [Publication 718-A](https://www.tax.ny.gov/pdf/publications/sales/pub718a.pdf) (12/25) for the rate history (Suffolk County's rate rose from 8⅝% to 8¾% on March 1, 2025; no other combined rate changed from 2022) | `scripts/local_sales_tax_rates/ny_pub718.csv` transcribes Publication 718; the build checks each rate and reporting code against the publication's text | No licence is attached. The Department's [website disclaimer](https://www.tax.ny.gov/help/tech/disclaimer.htm) provides the site "as a public service" and states no reuse restriction. The rates are facts set by the Tax Law. |
| Virginia | Virginia Department of Taxation, [Sales and Use Tax Rates by Locality by Date](https://www.tax.virginia.gov/sites/default/files/inline-files/sales-and-use-tax-rates-by-locality-by-date.xlsx), the "General Sales" rate of each county and independent city for each period | The workbook as downloaded | No licence is attached. The [website disclaimer](https://www.tax.virginia.gov/website-disclaimer) offers the site's information "as a public service to the taxpayers of the Commonwealth"; the site footer reads "Copyright © 2019 Virginia Department of Taxation. All rights reserved." The rates are facts set by Code of Virginia title 58.1. |

## Places and populations

| Source | Files | Terms |
|---|---|---|
| U.S. Census Bureau, [2020 Census Redistricting Data (P.L. 94-171) Summary Files](https://www2.census.gov/programs-surveys/decennial/2020/data/01-Redistricting_File--PL_94-171/): each tabulation block's county, county subdivision, place and total population (POP100) | `{st}2020.pl.zip`, geographic header file | Work of the U.S. Government, not subject to copyright in the United States (17 U.S.C. 105). |

## Method

- **SST states.** A boundary record's combined rate sums the rates of the
  jurisdictions it lists: the state (when its state indicator equals the
  state code), its county, its place, and up to 20 special taxing districts.
  A taxing unit is a county and the place code its records carry; its rate is
  the mean over its records, so a district covering part of a unit counts in
  proportion to the records it covers. Each unit uses its finest record type
  (address, else ZIP+4, else 5-digit ZIP). Rates are evaluated on every
  quarter start from 2022 through 2026 and on every other date in that window
  on which a state's files show a change.
  This record-weighted mean can include a small special taxing district
  within a city: Wichita (county 20173, place 79000), for example, is
  7.506% in the shipped data, compared with the ordinary 7.5% rate from the
  state and county. The build retains every applicable district; it applies no
  minimum record-share cutoff. The resulting city estimate need not be
  the rate at a particular address.
- **Place codes.** A unit's place code is matched to the 2020 Census place
  or county subdivision of its county with that code (in Vermont, whose
  local option taxes are levied by towns, to the town). A code that matches
  none is recoded to the Census entity of its county named like the postal
  city of most of its records, or else to the code that the same ZIP codes
  and postal cities carry after its records end, unless that entity has
  records of its own on the date. Georgia codes the DeKalb County part of
  Atlanta 05000 rather than 04000, and Vermont's 2022 records carry town
  codes it replaced in 2023. `manifest.json` logs every recoding and every
  code left unmatched; an unmatched code's area takes the rate of the place
  or county around it.
  Vermont's 2022 code 61225 is explicitly recoded to Rutland town 61300 even
  though the old code resolves to Rutland city. The city receives its known
  6% state-only rate in 2022, before its July 2023 local-option tax, with zero
  synthetic records so record-weighted averages do not change.
- **Blocks to places.** Each 2020 Census block takes the rate of its place's
  unit, else its county subdivision's, else its county's unit without a
  place code. A place's rate is the population-weighted mean of its blocks'
  rates, and so is the rate of a county's area outside every place.
- **Household geography.** Both the combined-rate and IRS-table lookups
  normalize county and place codes and accept a place GEOID only when its
  state matches the household. When county FIPS is absent, the block's
  county takes precedence over an explicitly entered county enum. An
  explicitly entered New York City or Yonkers flag identifies its place
  when place FIPS is absent. A place with no county uses its principal
  county: the county containing the largest 2020 Census population slice,
  with the smaller county FIPS code breaking ties. This mapping is built
  from all Census blocks before rate pruning. Elsewhere in the 50 states and
  DC, the Census place list resolves places lying in exactly one county;
  a place spanning multiple counties requires an entered county or block.
  Without any location
  signal, calculated county/city defaults are ignored and the existing
  state fallback applies. Explicit county and place codes take precedence.
- **Pruning.** A place whose rate equals the rate outside places in its
  county at every date is dropped, and its population is added to the
  county's remainder: a household there takes the same rate.
- **Known limits.** Iowa's boundary file has carried no place codes since its
  2024 rebuild, so from mid-2024 Iowa's local option taxes, which cities and
  unincorporated areas levy separately, are averaged over each county: a
  place without the tax gets part of it, and Des Moines gets Polk County's
  6.83% rather than 7%. Vermont's town taxes reach households through Census
  places: a household in a taxing town but outside every place takes its
  county's population-weighted rate outside places. Utah's files, ZIP+4
  records only, carry no city names, so a few state-assigned Utah codes stay
  unmatched (listed in `manifest.json`).
  Wisconsin's file added address records in late 2023; before then its
  ZIP+4 records apply the lowest rate in each ZIP+4 area, as SSUTA section 305
  requires.
  Vermont's uncoded 2022 statewide SST unit also includes a small share of
  local-option records, giving 6.0059% (6.0091% from October) where that unit
  applies. The build checks every coded municipality against the official
  list and logs municipalities with no coded unit, including Montgomery;
  these uncoded and county-remainder limits remain.

## Mississippi methodology awaiting a ruling

The [2025 IRS selector (PDF p. 18)](https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=18)
names Tupelo and Jackson without an other-locality row. The existing
documented Jackson-table proxy is retained pending Max's methodology
decision. For an $85,000 single filer with an entered 8% combined rate,
the 7% state component leaves 1 percentage point local: the proxy gives
Table C's $179 × 1 = $179.

The alternative reading applies the absent-local-table instruction
([PDF pp. 4–5](https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=4))
to other Mississippi localities, giving line 2 = 0 and the ratio method:
$1,243 × 1 / 7 = $177.57. That implementation would need an absent-table
signal and ratio routing as well as removing Mississippi from the default
table lists. No interpretation is selected here. Without an entered rate,
both readings give $0 because this build has no Mississippi locality rates.
