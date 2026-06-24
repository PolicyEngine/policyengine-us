# ZIP code-level HUD payment standards

## What

`zip_code_payment_standards.csv` holds Housing Choice Voucher payment standards
that a public housing authority (PHA) has **published and adopted** at the
ZIP-code level, indexed by `(zip_code, year, bedrooms)`. Because these are the
PHA's adopted standards — already reflecting its chosen point within HUD's
90-110 percent of Fair Market Rent band — they feed `pha_payment_standard`
directly and take precedence over Small Area FMRs and county FMRs.

The model variable `zip_code_payment_standard` reads this CSV; values are
monthly dollars and the variable multiplies by 12. Bedrooms above the published
maximum add 15 percent of the top value per additional bedroom.

## Scope today

- **Texas — TDHCA**: the Texas Department of Housing and Community Affairs
  administers the Housing Choice Voucher program in counties without their own
  local housing authority. The bundled schedule is TDHCA's 2025 payment
  standards covering 284 ZIP codes across 34 counties (the suburban/rural ring
  around the major metros, plus Waco and scattered central Texas).
- **Texas — Houston Housing Authority (HHA)**: Houston is not a mandatory-SAFMR
  metro, so HHA sets its own SAFMR-informed tiered schedule (effective
  2025-01-01). ZIP codes map to five tiers (A-1, A-2, B, C, D); in this edition
  the two A tiers share one set of amounts (e.g. 2BR $1,628) and B/C/D share a
  lower set (2BR $1,357). The bundled schedule covers 144 Houston ZIPs; 8 ZIPs
  that HHA only partially covers are already in the TDHCA rows and keep their
  TDHCA values.

The mandatory-SAFMR metro cores (Dallas, Tarrant, Bexar, Beaumont-Port Arthur)
are instead covered ZIP-by-ZIP via the Small Area FMRs in
`../fmr/small_area_fair_market_rents.csv`. Other states' published PHA schedules
can be appended to the same CSV.

## Schema

| column | type | meaning |
|---|---|---|
| `county` | str | county name (provenance only; lookup is by ZIP) |
| `zip_code` | str | five-digit ZIP code |
| `year` | int | schedule year |
| `bedrooms` | int | 0 through 6 |
| `value` | float | monthly payment standard in current-year dollars |

## Source

- TDHCA Section 8 Housing Choice Voucher program:
  <https://www.tdhca.texas.gov/section-8-housing-choice-voucher-program>
- "2025-Payment Standard-HCV" schedule (TDHCA, published 2025-01-24).
- Houston Housing Authority (Housing Alliance HTX) Payment Standards and ZIP
  code list, effective 2025-01-01:
  <https://housingforhouston.com/residents/housing-choice-voucher/payment-standards/>
- Regulatory citation: 24 CFR §982.503 (HCV payment standards, 90-110 percent
  of the applicable FMR).
