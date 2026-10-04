# California LIHEAP regular heating support

`ca_liheap_utility_heating` estimates the regular gas/electric utility HEAP
schedule for all 58 California counties. It is an annual SPM-unit amount.
FY2026 is the researched season. Undated formulas and parameter backfilling
produce unverified historical estimates for earlier years; they do not extend
verified coverage. FY2027 evidence acquired during research was a draft.

Regular wood/propane/oil assistance remains within the requested program scope,
but is not yet calculated. Local energy-burden group thresholds are unresolved;
wood valuation also requires local cord prices and heating-degree-day treatment.
The utility output is not a total California LIHEAP award. A zero utility
component for WPO or other unsupported fuels does not establish ineligibility
for regular assistance. No generic `ca_liheap` final award is provided. Solar,
coal, OTHER and UNSPECIFIED fuels have no supported utility-table crosswalk.

## Supported calculations

- Qualified household size counts citizen/legal-immigrant SPM-unit members.
  Income includes excluded nonqualified members. The SPM unit approximates the
  actual group sharing home energy costs.
- Earnings of members under 18 are excluded. Existing net business inputs
  include non-SSTB/SSTB, Schedule F farm operations and partnership/S-corporation
  income. No additional business-expense deduction is applied. Reported rental
  and farm-rental income are assumed nonnegative.
- Federal SSI and California SSP are aggregated from monthly values. CalWORKs
  is included once as the annual state benefit. Pension and retirement-account
  aggregates include their components once; non-SSA survivor benefits remain
  separate. SNAP affects categorical eligibility but is not countable income.
- Mandated support paid and reported allowable medical-insurance premiums are
  deducted. Per person, positive `health_insurance_premiums` takes precedence
  over `health_insurance_premiums_without_medicare_part_b`; they are not summed.
  Modeled Medicare premiums are not added: their deduction is deferred under
  the agreed implementation scope.
- CalFresh/SNAP or CalWORKs receipt bypasses the SMI income ceiling. An
  over-ceiling categorically eligible household always uses poverty group 4,
  including large households whose ordinary group-4 interval is empty.
- The utility award is county/group base amount plus $19 for each additional
  qualified member through size 6. There is no unsupported actual-bill cap,
  utility vulnerability supplement or statewide priority cutoff.

## Guideline reuse and rounding

The federal `fpg` helper uses a relative one-year lag, reproducing the 2025
guidelines used by the FY2026 matrix. Ordinary groups end at 100%, 125% and 150%
of FPG, rounded to monthly cents with ties upward. Boundary comparisons use
integer monthly cents to avoid float32 storage moving published boundaries.

The federal `smi` helper and shared four-person state amounts provide SMI. The
following inferred rounding reproduces all 25 explicit FY2026 matrix rows:

1. Truncate 60% of four-person annual SMI to a dollar: $128,144 × 60% → $76,886.
2. For sizes through 12, apply the federal size factor, truncate annual dollars,
   then divide by 12 and truncate monthly cents.
3. Above size 12, extend its $9,610.75 monthly amount by $192.215 per additional
   member, derived from the shared 3% factor, and truncate the result to cents.

The source does **not** explicitly prescribe this rounding or size-12 switch.
This is a numerical modeling inference, validated against every published row,
not a legal instruction. Sizes above 25 are unverified extrapolations. The
current agency income webpage instead says to add $192.21 after size 10; that
conflicts by cents with the final matrix starting at size 11. This implementation
follows the explicit final-matrix rows.

## Existing-input limitations

The application-period income rules require current monthly documentation;
annual inputs divided by 12 approximate steady income. Application timing,
identity, emancipation, temporary absence, live-in attendants, shared meters,
prior awards and local funding priority are not exactly represented. The
eligibility formula requires a qualified adult; it cannot identify an
emancipated minor who may legally apply.

Known utility heat with a positive matching expense establishes energy
responsibility. Unsubsidized heat included in rent is also allowed as a proxy
for a documented embedded charge. A subsidized household needs a reported
positive energy charge. Missing embedded-charge detail is an input limitation,
not a blanket legal prohibition on subsidized or heat-in-rent applicants.
County values use existing model geography, whose missing-county fallback can
select the first county in a state; accurate estimates need the actual county.

The raw premium totals do not distinguish vision, dental, long-term care and
all Medicare categories. Separately reported LTC and Medicare values are not
added or subtracted because their overlap with those totals is unspecified.
For exact calculations, the chosen raw premium input must represent allowable
non-Medicare medical coverage only. Otherwise premium deductions remain an
approximation. Alimony inputs also lack separate proof of a mandate.

Existing inputs cannot isolate income earmarked directly for housing, excluded
IHSS/live-in-aide earnings, interest retained rather than used for household
support, royalties, jury pay and some unusual insurance receipts. These are
mapping limits, not new income exclusions. General cash gifts, loans, capital
gains and in-kind assistance are omitted under the source exclusions.

## References

- [CSD final FY2026 LIHEAP State Plan](https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=6,7,9,182,183,184,185,186,187,188,193,196,202,203,205,217,218,219,229,230,231,232,233,234,235,236,237,238,239,240,243,244,245,246,247,248,249,250,257,279,363,364): utility matrix, eligibility guide and unresolved regular WPO rules.
- [CSD FY2026 income eligibility webpage](https://www.csd.ca.gov/Pages/LIHEAP-Income-Eligibility.aspx): larger-household rounding conflict.
- [CSD publication index](https://www.csd.ca.gov/Pages/LIHEAPProgram.aspx): final FY2026 and draft FY2027 status, checked October 3, 2026.
