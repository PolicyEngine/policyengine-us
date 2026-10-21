# California LIHEAP regular heating support

`ca_liheap_utility_heating` estimates the regular gas/electric utility HEAP
schedule for all 58 California counties. It is an annual SPM-unit amount.
FY2026 is the researched season. Undated formulas and parameter backfilling
produce unverified historical estimates for earlier years; they do not extend
verified coverage. Tested components do not establish a complete verified policy
year, so the partial registry entry has no `verified_years`. FY2027 evidence
acquired during research was a draft.

`ca_liheap_covered_liquid_heating` also estimates the ordinary propane/fuel-oil
component where local burden and priority rules have been verified: currently
Madera County. The statewide liquid base table is encoded, but that alone does
not establish coverage in other counties. `ca_liheap_wood_heating` estimates the
ordinary wood component throughout California when an approved eligible-delivery
cost is supplied. No output is a total California LIHEAP award; no generic
`ca_liheap` final award is provided. Solar, coal, OTHER and UNSPECIFIED fuels have no supported
utility-table crosswalk, and kerosene is not assigned a statewide liquid rule.

## Approved wood delivery

`ca_liheap_approved_wood_delivery_cost` is the approved cost of the eligible
ordinary wood, wood-pellet or manufactured-log delivery for the modeled program
year, before the ordinary benefit cap. Enter one program-year delivery amount,
not annual historical wood spending or an unrestricted vendor quotation. It
excludes any separately approved discretionary vendor-service supplement.

The approved amount already reflects the allowed quantity, fuel form, climate,
storage limits, reasonable pricing and administrative prioritization. Those
facts are supplied through the approved cost; the model does not independently
recalculate them. Company and agency identities are not distinguished. No cords,
provider, agency, heating-degree-day or storage inputs are required.

`ca_liheap_wood_heating` applies the shared income and qualified-adult checks,
requires primary `heating_type = WOOD`, and pays the nonnegative approved cost
up to the ordinary $1,000 WPO maximum. A positive approved cost establishes
heating-cost responsibility even if no past wood expense is reported. It does
not bypass the modeled income or qualified-adult requirements, and a wood quote
does not establish responsibility for a different primary heating fuel.

The input defaults to zero. Without a supplied approved cost the modeled wood
component is zero; this does not establish that the household is legally
ineligible. `wood_expense` alone does not produce a wood award. Neither the
quote nor the award is added to historical heating/utility expenses or the
energy-burden numerator. The wood component is not added to household benefit
aggregates. The approved-cost component was researched and tested for FY2026;
earlier-year backfills are unverified historical estimates.

## Liquid component coverage and interpretation

Always read `ca_liheap_liquid_heating_covered` alongside
`ca_liheap_covered_liquid_heating`:

- Coverage true: the ordinary liquid calculation is supported. A zero component
  then reflects a modeled basic-eligibility or local-priority failure.
- Coverage false: this component does not supply an award determination. Its
  numeric zero is the framework's out-of-coverage default, not a denial or a
  finding that the household has no regular heating entitlement.

Coverage requires propane or fuel-oil heating in Madera, positive countable
income, and an energy-cost/income ratio from zero through 100%. Zero-income and
above-100% burden assignments remain unresolved in the acquired local plan and
are expressly outside calculation coverage. Other counties and wood are also
outside the liquid component's coverage; the approved-cost wood component has
its own statewide calculation. The component is not added to household
benefit aggregates or substituted for the existing utility registry output.

The liquid schedule uses county/income-group base amounts, the shared $19
household increment through six members, burden additions of $0/$35/$70/$105,
and one $105 addition for a household containing a vulnerable member, capped
at $1,000. It represents the ordinary schedule without the conditional vendor
service supplement of up to $500; that supplement is not automatic and remains
unmodeled. There is no unsupported cap at annual or monthly fuel spending.

Madera's burden intervals are 0–10.92%, 10.93–13.46%, 13.47–16.00%, and
16.01–100%. Percentages are truncated to two decimal places, as required by the
state guide. The calculation restores monetary cents before classification to
avoid binary float storage moving exact boundaries. Existing annual electricity,
natural-gas, wood, propane and fuel-oil costs divided by annual countable income
approximate the current-month ratio; they cannot isolate arrears, climate
credits or the duration of a seasonal delivery receipt. Only the canonical
`gas_expense` is counted, never both it and the deprecated gas input.

Madera assigns income-group points of 10/8/6/4, burden-group points of 4/6/8/10,
and household demographic points: 10 for a child under six, an additional five
for a child under three, 10 for someone age 60+, an additional five for someone
age 70+, and 10 for disability. Each category counts once. The minimum is
20 points. These local thresholds are not extrapolated to other service areas.
The local plan has board-adoption evidence; a separate state approval letter
was not recovered.

`ca_liheap_basic_eligible` shares the existing qualified-adult, income and
energy-responsibility checks across utility, liquid and approved wood calculations. It does
not itself determine local priority or fuel eligibility. The existing utility
schedule and its documented limitations are preserved.

## Supported calculations

- Qualified household size counts citizen/legal-immigrant SPM-unit members.
  Income includes excluded nonqualified members. The SPM unit approximates the
  actual group sharing home energy costs.
- Earnings of members under 18 are excluded. Existing net business inputs
  include non-SSTB/SSTB, Schedule F farm operations and partnership/S-corporation
  income. No additional business-expense deduction is applied. Reported rental
  and farm-rental income are assumed nonnegative.
- Federal SSI and California SSP are aggregated from monthly values. CalWORKs
  is included once through the take-up-gated `tanf` aggregate. Unemployment uses
  `total_unemployment_compensation`, which reads reported compensation or modeled
  state benefits when none is reported. Pension and retirement-account
  aggregates include their components once; non-SSA survivor benefits remain
  separate, as does `military_retirement_pay`. Military survivor annuities remain
  part of the deferred cross-state retirement-input update. SNAP affects
  categorical eligibility but is not countable income.
- Mandated support paid and reported allowable medical-insurance premiums are
  deducted. Per person, positive `health_insurance_premiums` takes precedence
  over the decomposed non-payroll sum of
  `health_insurance_premiums_without_medicare_part_b` and
  `medicare_part_b_premium`. The disjoint `pre_tax_health_insurance_premiums`
  input is added in either case. This includes Medicare premiums once and
  respects the source's deduction from total gross income, without an SSA cap.
- CalFresh/SNAP or take-up-gated CalWORKs receipt bypasses the SMI income ceiling.
  Income strictly below 110% of the lagged federal poverty guideline also passes
  the income test, with the federal floor rounded to cents. The published SMI
  limit remains unchanged, and all qualified-adult and heating-cost gates remain.
  At 25 people the FY2026 SMI limit is $145,314.48, below the protected $162,415
  floor; income exactly at the floor does not receive this protection. An
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
all Medicare categories. For exact calculations, direct, decomposed and payroll
premium inputs must represent allowable medical coverage only, excluding vision,
dental, long-term care, reimbursement accounts and other excluded charges. A
positive direct non-payroll total must already contain any Medicare premium;
otherwise use the non-Part-B input and the separate Part B premium. No separate
LTC amount is added. These input-composition limits keep deductions approximate.
Alimony inputs also lack separate proof of a mandate.

Existing inputs cannot isolate income earmarked directly for housing, excluded
IHSS/live-in-aide earnings, interest retained rather than used for household
support, royalties, jury pay and some unusual insurance receipts. These are
mapping limits, not new income exclusions. General cash gifts, loans, capital
gains and in-kind assistance are omitted under the source exclusions.

## References

- [CSD final FY2026 LIHEAP State Plan #page 6-7,9-10,182-188,193,196,202-203,205,217-219,229-240,243-250,257,279,282-283,363-364](https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=6): utility/liquid matrices, ordinary WPO cap, wood quantity/pricing, eligibility guide and approved vendor payments.
- [CSD FY2026 income eligibility webpage](https://www.csd.ca.gov/Pages/LIHEAP-Income-Eligibility.aspx): larger-household rounding conflict.
- [CSD publication index](https://www.csd.ca.gov/Pages/LIHEAPProgram.aspx): final FY2026 and draft FY2027 status, checked October 3, 2026.

- [Madera FY2026 local plan, October 9, 2025 board packet #page 191,233-234](https://maderacap.org/wp-content/uploads/2025/10/Agenda-and-Packet-for-October-9-2025-Updated.pdf#page=191): local burden bands, priority points and minimum.
- [Madera November 13, 2025 board packet #page 4,6](https://maderacap.org/wp-content/uploads/2025/11/Agenda-and-Board-Packet-November-13-2025.pdf#page=4): October 9 minutes, consent-calendar approval including item D17.
