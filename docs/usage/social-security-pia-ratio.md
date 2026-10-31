# Population Social Security PIA ratio

The reported-benefit route implements design v3 C1–C3, with A1's factor
composition, A5.2's record/proxy distinctions, P2's annual cross-section
convention, and amendments M2, M4, M8 and M9. It approximates a formula reform
for benefits already in payment. It does not reconstruct a worker's earnings
history or establish benefit entitlement.

For each annual Person component `X` (`retirement`, `disability`,
`survivors`, `dependents`), the population lever applies

```text
z = reported_X / (12 * a * s * baseline_COLA(E, t))
factor_X = new_PIA(inferred_AIME, E; t) / baseline_PIA(inferred_AIME, E)
```

The public formula multiplies the reported base by this factor, the joint COLA
factor, the across-the-board factor and the payable factor. Calculated source
routes compute their PIA and COLAs directly and bypass these population
factors. An initial public-name input is migrated to its `_reported` twin,
including public-name dataset columns in the scoring year; a later explicit
public write is a final override. See the benefit-lever ingress documentation.

The forward PIA calculations and inverse use the same service as the
[supplied-record calculator](social-security-calculator.md).
`bend_points_at` selects the original eligibility-year bend points;
`formula_path_at` supplies the combined reform and its `recompute_mode`.
C does not add a second retroactive-recomputation switch. The inverse always
uses the fixed unreformed formula and the unreformed reported amount.

## Supplied claim age and explicit scenarios

`social_security_retirement_claim_age_months` is a pure annual Person input:
age in whole months at first entitlement, so 62 years 3 months is 747.
It has no formula, uprating, or positive-amount selection rule. A projected H5
may store this column like any other input, with a value for each scoring year.

`gov.contrib.ssa.benefit_levers.pia_ratio.claiming_scenario` explicitly selects:

| Value | Claiming adjustment source |
|---|---|
| `supplied_claim_age` (default) | The supplied age in whole months. |
| `entitlement_dates` | Component entitlement year/month and supplied birth date. |
| `age_62` | Sensitivity assuming age 62. |
| `age_65` | Sensitivity assuming age 65. |
| `fra` | Sensitivity assuming cohort full retirement age. |
| `age_70` | Sensitivity assuming age 70. |

Core represents these named selector parameters as singleton lists. For example,
set `claiming_scenario` to `[age_65]` and `disability_eligibility_proxy`
to `[current_year]` in a parameter reform; the adapter reads the one selected
name. Bare scalar strings are unsupported by Core's parameter schema.

All scenarios preserve cohort FRA, early months and delayed-credit rates.
Under `supplied_claim_age`, a missing value, a value before 62, or a value
after 70 leaves the affected factor at one and raises
`_pia_ratio_missing_claim_age`. There is no silent change to another scenario.
The `entitlement_dates` scenario uses the entitlement year/month and birth
year/month. Supply `social_security_birth_month`; the optional
`social_security_birth_day` refines SSA age attainment. With a known birth
month and no day, day 2 is the explicit within-month convention and
`_pia_ratio_proxy` is true. Zero birth month means unavailable. A complete
`ss_calculator_birth_date` supplies the exact date instead; exact dates
preserve attainment on the day before a birthday, including January 1 births.

Where only a birth year is available for an age-month scenario, the cohort
calculation uses the documented non-January-1 approximation and raises
`_pia_ratio_proxy`. Exact birth information and an explicitly supplied
`birth_year` take precedence over a year derived from current age. When birth
information is unavailable but a worker eligibility year is supplied, E minus
62 can supply the approximate birth cohort for FRA and credit rates; this does
not change the supplied eligibility year. Supplied month/day without an
observed birth year or complete birth date still raises the proxy flag.
A claiming scenario is substantive:
in C2, replacing the
correct age-62 adjustment of 0.70 with 1 infers AIME $2,978 instead of $5,000
and changes the annual gain from $1,165.248 to $1,664.64 before rounding, an
overstatement of about 43%.

## Eligibility years and auxiliary identification

Supplied `social_security_X_worker_eligibility_year`,
`social_security_X_worker_id` links and the underlying worker's
`social_security_worker_computation_year` precede proxies. A supplied
entitlement/onset year supplies the component's applicable basis where
appropriate. A link must identify an existing Person and a supplied computation
basis; conflicting record years are unsupported.

For own retirement, a supplied worker eligibility year takes precedence. Without
one, exact birth information or an explicitly supplied `birth_year` identifies
the age-62 eligibility year before the current-age proxy; known entitlement
dates and a supplied observed claim age can also identify that year. If none of these
supplies a basis, each scoring year's proxy is `E = t - age_t + 62`. Rebuild
it independently for every annual cross-section. A row whose age stays 70 and
has no supplied basis has E=2018 in 2026 and E=2027 in 2035;
the model does not carry an inferred cohort or claiming history between those
rows. Integer age also leaves birthday/within-year ambiguity, so compare adjacent
eligibility years when scoring sensitivities.

Disability uses `a = 1` and a supplied onset, entitlement or worker computation
year when available. Missing onset is explicitly controlled by
`gov.contrib.ssa.benefit_levers.pia_ratio.disability_eligibility_proxy`:
`pre_reform` is the upper-exposure assumption, using a supported benchmark
before the active reform; `current_year` assumes newly entitled in the scoring
year. Both are labelled proxies, not observed onset histories.

For survivors and dependents, a recipient age cannot identify the underlying
worker's PIA. A supplied worker link/year alone does not establish the share.
The identified auxiliary route also requires:

- `social_security_X_worker_benefit_ratio`: the composite `a * s`, including
  every applicable claiming adjustment and recipient share/reduction.
- `social_security_X_worker_ratio_identified`: an explicit assertion that this
  is one identified worker PIA, with no unaccounted dual entitlement, binding
  family cap or earnings-test withholding.

For reported retirement, a record that also has positive reported survivor,
dependent or disability amounts remains unmodeled for this lever. The mixed
recipient amounts do not identify whether retirement is one full worker PIA,
dual entitlement or a partial-year conversion.

The inversion divides by that composite ratio once. Without a supported
worker basis and identified ratio, the amount keeps factor one and raises
`_pia_ratio_unmodeled`. No recipient-age worker proxy is enabled by default.
For this composite route, the named claiming-adjustment output is one as a
decomposition convention: the entire supplied `a * s` is assigned to the
worker-benefit ratio. This does not establish that the underlying worker
claimed at FRA or identify `a` separately.
The restricted supplied-ratio survivor household calculator retains its own
more detailed record-basis and nonbinding-limit assertions.

When S.770 is active, reported survivors additionally require the same
recipient-side `ss_calculator_*` computation-basis fields as the household
route: worker birth year and death year, basis provenance, prior-disability
declaration, ordinary non-WINDEX assertion, and the applicable exact dates or
year-only/same-year assertions. An authoritative computation year is required
for prior disability. The basis must agree with the supplied worker eligibility
or computation year. Missing identification leaves factor one and raises
`_pia_ratio_unmodeled`; contradictory supplied information is rejected.
For a pre-2026 death before age 62 with no prior disability eligibility, the
existing S.770 interpretation switch controls only the 18% first-bend-point
increase. The 95% first factor applies with either switch value.

Supported benchmark years start in 1983. A positive record with an earlier
benchmark keeps factor one and raises `_pia_ratio_pre_1983`. The initial PIA
rounding rule before 1983 is outside this inverse's scope. COLAs accumulate
from eligibility, including pre-claim COLAs, using the unreformed statutory
ledger; they do not use benefit-income uprating or reformed COLAs.

## Named annual outputs

Replace `X` below with any of the four component names. Monetary outputs are
monthly dollars at the eligibility-year valuation basis, even though the
reported source benefit is annual.

| Person variable suffix after `social_security_X` | Meaning |
|---|---|
| `_inferred_aime` | Baseline inverse of the observed amount; the lower-endpoint convention for an exact dime-rounded eligibility PIA. |
| `_inferred_aime_lower_bound` | Inclusive conditional AIME interval bound. |
| `_inferred_aime_upper_bound` | Exclusive conditional AIME interval bound. |
| `_pia_ratio_eligibility_year` | Underlying worker eligibility/computation year E. |
| `_pia_ratio_claiming_adjustment` | Imputed worker claiming adjustment a; zero means unavailable on a positive retirement record, while one is the auxiliary composite-ratio decomposition convention. |
| `_pia_ratio_own_record_retired_worker` | Own-record retired-worker indicator. |
| `_pia_ratio_missing_claim_age` | Required claiming information is unusable. |
| `_pia_ratio_pre_1983` | Benchmark predates supported initial-PIA rounding. |
| `_pia_ratio_unmodeled` | This amount lacks a supported identified inversion. |
| `_pia_ratio_proxy` | An eligibility, birth or claiming approximation was used, including every resolved `age_62`, `age_65`, `fra` or `age_70` sensitivity even with an exact birth date. |
| `_pia_ratio_measurement_uncertainty` | Annual reported measurement is not an exact eligibility PIA. |

Zero monetary outputs on records without an inference are placeholders.
Inspect the flags before interpreting them as zero earnings. The own-record
indicator describes the modeling classification; it is not evidence of insured
status or an administrative validation of benefit type. It is independent of
whether claiming data are missing or the benchmark predates 1983. For an AIME
distribution computed from these outputs, also exclude `_pia_ratio_unmodeled`,
`_pia_ratio_missing_claim_age` and `_pia_ratio_pre_1983` records and inspect
the proxy and measurement-uncertainty flags.
For identified-only distributions, also exclude `_pia_ratio_proxy` records;
report their sensitivity results separately. The named AIME outputs include
supported proxy inferences, so this filter must be applied by the consumer.

On a positive retirement record, claiming adjustment zero is an unavailable
diagnostic sentinel until the selected scenario yields a usable adjustment.
Missing claiming data and unsupported pre-1983 records can therefore report
zero while keeping the benefit factor at one. Do not interpret this sentinel
as an actuarial factor, a complete benefit cut, or a default FRA assumption;
filter the associated flags. Disability keeps adjustment one, auxiliary
composite ratios use one by decomposition convention, and a zero-benefit
record keeps the neutral adjustment one.

For exact dime-rounded baseline eligibility PIA z, the interval is
`[inverse(z), inverse(z + 0.10))`; the point estimate is its lower endpoint.
C2's $2,156.80 baseline PIA therefore gives
`[5000, 5000.3125)`. When the source is a rounded paid benefit or a survey
annual amount, that narrow interval is conditional on the assumed measurement
basis. It does not quantify all survey error.
`gov.contrib.ssa.benefit_levers.pia_ratio.annual_rounding_bound` optionally
supplies a nonnegative symmetric annual-dollar bound for
`[max(0, b - bound), b + bound)`, propagated backward through the baseline
divisor, with one dime of initial PIA truncation added at the upper endpoint.
The point estimate continues to invert the observed amount; it does not move
to the lower endpoint of this wider measurement interval. The default zero
adds no annual measurement-resolution assumption; it does not certify exact
data.

Core stores monetary input arrays as float32. Before exact arithmetic, the
adapter uses each stored scalar's shortest float32 decimal representation.
This avoids expanding binary representation noise into an additional PIA
dime; it does not round every annual source to cents or recover precision
already lost when the input was stored.

Named AIME point estimates and interval bounds are stored at Core's float32
resolution. The adapter rounds them toward positive infinity so an ordinary
cast cannot move a lower endpoint below the baseline inverse. Represented
values can differ from the mathematical endpoint by up to one float32 step;
use the shared pure service for exact interval membership or boundary
calculations. It keeps rational endpoints internally, and the shared
`PIAInverse` exposes exact Fraction bounds as well as high-precision decimals.

A zero benefit produces factor one and zero monetary outputs without division.
Negative reported amounts and nonpositive divisors are unsupported and rejected.
Factors cannot be negative. With every PIA reform off, factors are exactly one.

## Weighted counts and scoring limits

For any Person indicator `flag`, the authoritative weighted count is

```text
sum(flag_i * person_weight_i)
```

The associated unmodeled annual amount is
`sum(flag_i * social_security_X_reported_i * person_weight_i)`.
Apply weights once. Report identified results, proxy sensitivities and unmodeled
amounts separately.

Household variables `social_security_X_pia_ratio_FLAG_count` are also available
for `FLAG` equal to `missing_claim_age`, `pre_1983`, `unmodeled`, `proxy`
or `measurement_uncertainty`. They sum the corresponding Person indicators
within a household. A normal weighted household aggregation gives the weighted
count when members use the household weight. If an artifact supplies distinct
Person weights within a household, use the Person-indicator formula above.

This approximation assumes the reported annual amount represents a full-year
benefit at the stated valuation basis; partial-year entitlement, survey error,
dual entitlement, withheld checks and binding caps can defeat unique inversion.
PE-US encodes no package-specific parameter values and estimates no percentile.
The named outputs above remain available for population diagnostics and drift
checks.

## Price-indexing inputs you supply

PE-US ships no values for either price-indexing path, and both are off by
default. The reported-benefit ratio and the
[supplied-record calculator](social-security-calculator.md) read the same
parameters through `formula_path_at`. To turn on progressive price indexing,
set these parameters under `gov.contrib.ssa.pia`:

| Parameter | What you supply |
|---|---|
| `in_effect` | `true` for the eligibility cohorts the formula path reaches. |
| `progressive_price_indexing.in_effect` | `true`. |
| `progressive_price_indexing.start_year` | The first eligibility cohort indexed. The default is 2032. |
| `progressive_price_indexing.bend_point_fraction` | The fraction f of the way from the first to the second bend point. It has no default. |
| `progressive_price_indexing.threshold` | Optional: a monthly dollar threshold for each cohort. Where you set one, it takes precedence over the fraction. |
| `progressive_price_indexing.maximum_aime` | The monthly maximum-career AIME for each cohort. |
| `progressive_price_indexing.maximum_pia_target` | The target initial monthly PIA at that maximum AIME for each cohort. |

For eligibility year E, the protected threshold is
`T(E) = BP1(E) + f * (BP2(E) - BP1(E))`, using that cohort's own bend points,
so it rises as they do. With f = 0 it equals BP1, and with f = 1 it equals BP2.
Below the threshold the current-law formula applies unchanged. Above it, the
model scales the part of the PIA above `F(T(E))` by the single multiplier that
makes the PIA at the maximum AIME equal the target.

The fraction is an ordinary dated parameter and holds forward like any other.
The dollar threshold, maximum AIME and target need an entry dated January 1 of
each cohort's eligibility year, and an earlier cohort's entry never serves a
later one. Full price indexing likewise needs `full_price_indexing.in_effect`,
its `start_year`, and a `real_wage_scale` dated for each cohort.

Your reform settings supply the fraction or dollar path and the maximum AIME
and target paths; PE-US computes none of them. With progressive indexing on,
a cohort with neither a fraction nor a dollar threshold, or without its
maximum AIME or target, raises an error rather than falling back to current
law. The fractions in the PE-US tests are illustrative and make no claim about
any percentile.

```python
from policyengine_core.reforms import Reform

# Illustrative values for one 2035 cohort. Add a maximum AIME and target
# for every cohort the score reaches.
reform = Reform.from_dict(
    {
        "gov.contrib.ssa.pia.in_effect": {"2032-01-01": True},
        "gov.contrib.ssa.pia.progressive_price_indexing.in_effect": {"2032-01-01": True},
        "gov.contrib.ssa.pia.progressive_price_indexing.start_year": {"2032-01-01": 2032},
        "gov.contrib.ssa.pia.progressive_price_indexing.bend_point_fraction": {"2032-01-01": 0.25},
        "gov.contrib.ssa.pia.progressive_price_indexing.maximum_aime": {"2035-01-01": 17_000},
        "gov.contrib.ssa.pia.progressive_price_indexing.maximum_pia_target": {"2035-01-01": 5_100},
    },
    country_id="us",
)
```
