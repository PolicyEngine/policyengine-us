# Locality sales tax rates: sources and terms

`rates.csv` and `populations.csv` are built by
`scripts/local_sales_tax_rates/build.py` from official state files only. Where
PolicyEngine has no official locality rates, it applies no local rate: the
combined rate defaults to the state rate in the IRS state table heading, and
users can enter their own combined or local rate.

`rates.csv` holds the combined state and local general sales tax rate
(general intrastate rate) of each county's places with their own rate and of
the county's area outside them, from 2022, and `populations.csv` the 2020
Census population of each. `state_rates.csv` holds each covered state's
general sales tax rate (worksheet line 3 is the combined rate less it),
except Nevada's: its files fold the state rate into county rates, and the
IRS has Nevada residents enter the combined rate above the 6.85% heading. They carry only rates and Census codes derived from the sources below,
not the sources' files.

Retrieved 2026-10-06 (from 11:00 UTC). `scripts/local_sales_tax_rates/manifest.json` lists the
SHA-256 of every input file and the build log.

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
- **Blocks to places.** Each 2020 Census block takes the rate of its place's
  unit, else its county subdivision's, else its county's unit without a
  place code. A place's rate is the population-weighted mean of its blocks'
  rates, and so is the rate of a county's area outside every place.
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
