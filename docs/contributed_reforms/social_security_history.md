# Social Security annual earnings histories

The opt-in household calculator accepts an annual covered-earnings history
with `ss_calculator_source: history`. It computes conventional AIME and the
initial eligibility PIA, with optional owners' draw credit, annual mini-PIAs,
and a separate above-cap AIME+ component. All reforms are off by default.
Insured status is supplied explicitly; this route does not calculate credits
or disability, family, survivor, or minimum benefits.

The existing supplied-AIME, supplied-PIA, and restricted-survivor routes remain
available. Calculated `ss_calculated_*` outputs remain separate from reported
public Social Security benefits, following the merged household calculator's
interface. The history selector does not replace a public benefit input.

## Annual source and missing years

`ss_calculator_earnings_history` is one JSON string containing the complete
source record. Keeping the career in one structural input preserves all years
and supplied decimal amounts through source extraction and reload. It also
avoids treating Core's carry-forward of an annual scalar as a new earnings
observation.

The JSON object contains:

| Field | Meaning |
| --- | --- |
| `first_year` | First year enumerated by the history. |
| `records` | Annual observations with `year`, `covered_wages`, and `covered_self_employment`. Both monetary fields are required, including explicit zero. |
| `certified_zero_years` | Explicitly certified zero years omitted from `records`. |
| `certified_zero_before_first_year` | Certifies all earlier potential base years as zero. Required when `first_year` is later than the worker's birth year or 1951, whichever is later. |

Covered wages mean earnings in covered employment before the ordinary annual
cap. Existing covered self-employment means earnings after their existing
net-earnings adjustment, before the benefit cap. These are earnings amounts,
not tax liabilities. Amounts may be JSON numbers or decimal strings; strings
are useful when another application's JSON encoder would lose precision.

Every year from `first_year` through the year before initial entitlement must
be observed or certified zero. Missing years are rejected. Duplicate records,
overlapping observations and zero certificates, nonfinite amounts, and negative
covered earnings are rejected. Later observations may remain in the source
but do not enter the initial calculation: a claim in year Q uses earnings
through Q−1. Requesting a later benefit year does not recompute the initial
earnings record.

For example, a worker born in 1964, first eligible in 2026 and claiming in
2029 can supply the following JSON string. The certificate is an explicit
assertion about this synthetic worker's earlier earnings:

```json
{
  "first_year": 2026,
  "certified_zero_before_first_year": true,
  "certified_zero_years": [2027],
  "records": [
    {
      "year": 2026,
      "covered_wages": "60000.00",
      "covered_self_employment": "0.00"
    },
    {
      "year": 2028,
      "covered_wages": "65000.00",
      "covered_self_employment": "0.00"
    }
  ]
}
```

The calculator also requires the existing own-record fields: worker ID, exact
birth date, age-62 eligibility year, first entitlement month, insured-status
assertion, and assertions about unsupported special earnings tests and prior
withholding adjustments. The supported eligibility benchmark begins in 1983.

## Conventional AIME and the shared benefit pipeline

For eligibility year E and initial claim year Q:

1. Include annual earnings through Q−1, including earnings after age 62.
2. Cap each year's covered wages plus existing covered SE plus enabled owners'
   draw credit at that earnings year's ordinary contribution and benefit base.
3. For a year y before E−2, multiply by `NAWI(E−2) / NAWI(y)` and round to
   cents, with half cents rounded upward. Earnings in E−2 and later remain at
   face value.
4. Select the highest 35 annual indexed amounts, pad with certified zeros,
   divide by 420, and floor to a whole monthly dollar.
5. Call the same eligibility-year `compute_pia` service used by supplied AIME.

The [POMS indexing procedure](https://secure.ssa.gov/poms.nsf/lnx/0300605018)
establishes the index year and cent rounding. The
[POMS AIME/PIA procedure](https://secure.ssa.gov/poms.nsf/lnx/0300605021)
specifies whole-dollar AIME and lower-dime PIA rounding for modern benchmarks.
The [initial base-year rules](https://secure.ssa.gov/poms.nsf/lnx/0300605017)
distinguish the initial calculation from later recomputations. This calculator
deliberately freezes earnings at initial claim; post-claim recomputation is
outside this deliverable.

The household payment service then applies eligibility-origin COLAs, the
claiming adjustment, contributed payment policies, rounding, and the earnings
test once. The [SSA COLA application sequence](https://www.ssa.gov/OACT/COLA/colaapplic.html)
truncates the PIA after a COLA and the claiming-adjusted amount to dimes,
followed by the applicable final payment rounding.

An entitlement month's check is normally paid the following month. Annual
entitlement and annual payments are separate totals. A January first
entitlement therefore normally produces 12 entitlement months and 11 checks
in that calendar year.

## Owners' draw credit

When E1 is enabled for an observed earnings year, its record must contain
`owners_draw` with all four signed fields: `s_corp_income`, `partnership_income`,
`passive_income`, and `already_se_income`, including explicit zero values.
Include `subsets_are_disjoint` or `passive_se_overlap` when required.
Certified-zero years supply zero owners' inputs automatically. The passive and
already-SE amounts are subsets already included in the entity totals.
`already_se_income` is a gross partnership source amount; it differs from the
record's adjusted `covered_self_employment`.

The history route and installed reform call one shared `compute_owners_draw`
kernel. Extracting the existing arithmetic preserves the reform's intermediate
outputs and input overrides while avoiding a second implementation. Annual
policy parameters govern activation, the phase-in share, netting, the separate
reporting floor, and wages/SE/draw room priority. See the
[owners' draw specification](owners_draw.md) for signed losses and overlapping
subsets.

The shared kernel retains the reform's existing floating-point and NumPy
intermediate arithmetic. The history adapter restores its monetary outputs
with `Decimal(str(...))`, then applies the history route's annual indexed-cent
rounding. This preserves the existing reform computation while keeping the
subsequent annual earnings ledger separate from Core's float32 input storage.

The default netting expression is
`1 − employer_share × (SE_OASDI_rate + SE_HI_rate)`, or 0.9235 at current rates.
The planned adjusted draw must independently meet the $400 net-earnings floor
at current settings. Enabled benefit credit adds accepted adjusted draw N_D
to annual covered earnings before the ordinary cap. It does not append N_D
to AIME or derive earnings by dividing a tax amount by a rate.

The `room_cap_basis` parameter preserves the current-law cap or explicitly
removes the draw ceiling. It changes the tax-side room; ordinary benefit
credit still follows the annual benefit cap and any separately enabled
above-threshold credit. The existing reform's active NIIT exclusion remains
`draw_oasdi_base / q` with OASDI only and the full actual gross draw with HI.

## Mini-PIA

The named `compute_mini_pia` function applies the same eligibility-year PIA
formula to each annual ordinary indexed covered amount divided by 12. It
selects the highest 40 annual mini-PIAs, pads shorter certified careers with
zeros, and divides their sum by 37. The divisor is always 37.

The archived [2025 OACT B3.12 description](https://www.ssa.gov/OACT/solvency/provisions_tr2025/benefitlevel.html)
says, “Sum these individual PIAs for the 40 highest years of indexed earnings
and divide that total amount by 37”. Its retired-worker phase-in is 20% in
2032, 40% in 2033, 60% in 2034, 80% in 2035, and 100% from 2036. Disability
benefits are unchanged. The independently enabled parameter path is under
`gov.contrib.ssa.history.mini_pia`.

**Modeling conventions:** retain precision in each mini-AIME and mini-PIA,
aggregate with /37, and blend
`mini_share_E × mini_PIA + (1 − mini_share_E) × conventional_PIA` before final
dime truncation. Conventional AIME/PIA retains its statutory rounding. Add
the separate AIME+ PIA after the blend, then truncate the combined eligibility
PIA to dimes. These intermediate rounding and composition choices come from
the calculator design; OACT's summary does not prescribe them.

## Above-cap AIME+ credit

Independent named parameter sets under `gov.contrib.ssa.history.donut` retain
the archived `oact_2025_e2_13` and `oact_2025_e2_14` provisions and a `custom`
set. Activation, threshold, start year, tax rate, credit flag/rate, and
inclusion of existing SE or reclassified draw are separate settings. A
credit-off variant can tax earnings while producing no AIME+ credit.

The archived [2025 OACT payroll-tax descriptions](https://www.ssa.gov/OACT/solvency/provisions_tr2025/payrolltax.html)
state E2.13 as “Apply OASDI 12.4 percent payroll tax rate on earnings above
$400,000” and E2.14 as “Apply OASDI 12.4 percent payroll tax rate on earnings
above $250,000”. Both begin with 2027 earnings and use a 2% secondary AIME+
factor. Their thresholds stay fixed; once the ordinary cap reaches the
threshold, the gap disappears.

For each enabled earnings year, the separate taxed stream is
`max(selected_covered_earnings − max(ordinary_cap, threshold), 0)`. The gap
between cap and threshold receives neither additional tax nor credit.
Earnings receive AIME+ credit only when the provision taxes them and enables
credit. Including existing SE or adjusted owners' draw applies consistently
to the tax and credit ledger.

Index the extra stream using the same E−2 convention, select its own highest
35 years, divide by 420 and floor to whole dollars. Multiply that separate
AIME+ by the credit rate and add it after the mini/conventional blend. This
stream never changes conventional AIME. These services expose hypothetical
annual tax/credit amounts for the household report; they do not change
population payroll-tax variables.

For a custom changing path, annual tax/coverage settings determine the extra
earnings stream, and the PIA credit coefficient is read at eligibility E.
This is a cohort-selection convention; the archived variants' coefficient is
constant at 2%. Pure callers whose credited annual streams use different
coefficients must supply the eligibility coefficient explicitly.

## Annual earnings ledger

`AnnualBenefit.history` exposes the typed history calculation to Python
callers. `ss_calculated_history_ledger` exposes its annual ledger as a JSON
string for a household report. The ledger retains ordinary covered earnings,
accepted E1 credit, the separate donut-taxed and credited stream, indexing
amounts, and each year's mini-PIA so the result can be reconciled by year.

The accompanying annual diagnostics are `ss_calculated_history_aime`,
`ss_calculated_history_aime_plus`, `ss_calculated_history_mini_pia`, and
`ss_calculated_history_conventional_pia`. These diagnostics preserve the
initial-claim earnings calculation when a later payment year is requested.
`ss_calculator_donut_variant` selects the named donut parameter set; its
default `custom` set is inactive until explicitly configured.

The annual report prices mini-PIAs and PIA diagnostics using January
entitlement's formula. Its income ledger stays frozen at Q−1. An exact fraction
accompanies recurring mini-PIA decimals, and highest-year selection flags use
the earlier earnings year to resolve ties. Before eligibility, the report
retains the earnings ledger and leaves PIA diagnostics unset.

## Reviewable arithmetic and compatibility

The synthetic 2036-eligibility fixture uses flat NAWI, zero COLAs, a $120,000
ordinary cap, $1,000/$6,000 bend points, and .90/.32/.15 factors. Thirty-three
$60,000 wage years and a $120,000 capped year give AIME $5,000 and PIA
$2,180.00. A $60,000 accepted gross draw contributes $55,410, giving AIME
$5,131 and conventional PIA $2,221.90. A $500,800 wage year contributes
$100,800 to the $400,000 donut stream: AIME+ $240 and PIA+ $4.80.

Annual minis are $2,180.00 for a $60,000 year, $3,100.00 for the capped year,
and $2,057.60 for the owners' year. The mini with E1 is
`(33 × 2180 + 3100 + 2057.60) / 37 = 2083.718918…`. Adding PIA+ and
truncating to dimes gives $2,088.50. Claiming 24 months before FRA uses
13/15 and pays $1,810 monthly, or $21,720 for 12 entitlement months.

Published conventional comparisons use SSA's
[annual earnings histories](https://www.ssa.gov/OACT/ProgData/retirebenefit1.html)
and [PIA examples](https://www.ssa.gov/OACT/ProgData/retirebenefit2.html).
The published 2027 Case A has AIME $6,072 and initial PIA $2,720.20. Case B
first eligible in 2022 has AIME $11,843, including later earnings through
2026, and initial PIA $3,419.60. Source data are fixed in the corresponding
test fixtures; the live SSA examples can advance to another retirement year.

The merged implementation takes precedence over older design descriptions:

- The existing `ss_calculated_*` interface remains separate from reported
  public benefits. Payment-year totals retain the merged one-month check lag.
- Runtime parameters already include historical bends and future wage-indexed
  paths. The history route reuses them, including future household claim years.
- Legacy `ss_aime` keeps its rolling lookback, age filters, and untruncated
  result. The opt-in complete-history route shares applicable arithmetic and
  is compared with it where those legacy assumptions match.
- One structural JSON source holds all annual observations instead of many
  period-specific inputs. Explicit certificates preserve missing-versus-zero
  semantics and make source export complete.

There are no package-specific settings, population impact estimates, insured
credits algorithm, or post-claim earnings recomputations in this interface.
