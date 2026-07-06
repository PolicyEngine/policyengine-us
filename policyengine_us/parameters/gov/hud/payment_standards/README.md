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
  lower set (2BR $1,357). The bundled schedule covers 146 Houston ZIPs; 9 ZIPs
  that HHA only partially covers are already in the TDHCA rows and keep their
  TDHCA values.

The mandatory-SAFMR metro cores (Dallas, Tarrant, Bexar, Beaumont-Port Arthur)
are instead covered ZIP-by-ZIP via the Small Area FMRs in
`../fmr/small_area_fair_market_rents.csv`. Other states' published PHA schedules
can be appended to the same CSV.

## Year coverage

Both bundled sources hold their **2025 schedule year only**, and
`nearest_payment_standard_year` therefore resolves period 2026 to the 2025
standards. This forward-imputation is intentional, not a missing-data gap:
as of 2026-07-06 neither PHA has adopted a distinct 2026 schedule.

- **TDHCA** publishes HCV payment standards annually; the latest posted on its
  Section 8 resources page is "2025-Payment Standard-HCV" (files run 2023, 2024,
  2025). No 2026 file exists (`26-HCV-PaymentStandards.pdf` and variants
  404).
- **Houston HHA (Housing Alliance HTX)** posts a "Payment Standards for 2026"
  PDF, but it is explicitly **Effective 01/01/2025** and its tier amounts and
  ZIP-to-tier assignments are identical to the 2025 schedule already bundled
  (verified: 0 differences across the 144 shared ZIPs, Tier A 2BR $1,628 /
  Tier D 2BR $1,357 unchanged). It is a re-titled carry-forward of the
  2025-effective schedule, not a new vintage.

Encoding a duplicate 2026 block would fabricate a distinct fiscal-year vintage
that neither PHA has published, so period 2026 continues to resolve to the
2025 rows. Add a real 2026 block once either PHA adopts new-dollar 2026
standards with a 2026 effective date.

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
- TDHCA Section 8 resources (payment-standard PDFs by year):
  <https://www.tdhca.texas.gov/section-8-resources>
- "2025-Payment Standard-HCV" schedule (TDHCA, published 2025-01-24):
  <https://www.tdhca.texas.gov/sites/default/files/section-8/docs/25-HCV-PaymentStandards.pdf>
  (retrieved 2026-07-06; latest published).
- Houston Housing Authority (Housing Alliance HTX) Payment Standards and ZIP
  code list, effective 2025-01-01:
  <https://housingforhouston.com/residents/housing-choice-voucher/payment-standards/>
  and the "Payment Standards for 2026" PDF (Effective 01/01/2025) linked from
  <https://www.alliancehtx.org/landlords> (both retrieved 2026-07-06).
- Regulatory citation: 24 CFR §982.503 (HCV payment standards, 90-110 percent
  of the applicable FMR).
