# Supplied-record Social Security calculator

The opt-in calculator implements design v3 D0, 4a-1 and the shared 4d core,
including amendments M1–M4, the top-factor structure in M6 and M8. It returns
**gross benefits before Medicare deductions**, from an identified worker record.
Existing public benefit inputs continue to work independently.

## Inputs and outputs

Set `ss_calculator_source` to `aime`, `pia` or `survivor`; its default is `off`.
The selector determines the route even when the selected amount is zero.
Omitting the selected amount fails; it is distinct from supplying zero.
Identity/source fields are eternal inputs. Supply exact recipient birth date,
worker ID, entitlement month, insured status and source valuation basis. The
only supported basis is `unreformed_eligibility`; externally reformed sources
fail rather than applying a mechanism twice. Each member of a retired couple
supplies their own record. Disability, spouse, child, minimum and dual-entitlement
computations are outside this route.

For own retirement, also supply `ss_calculator_eligibility_year` and either
`ss_calculator_supplied_aime` (whole monthly dollars) or
`ss_calculator_supplied_pia` (monthly dimes at initial eligibility). Optional
`ss_calculator_claiming_factor` is an exact decimal **string**; otherwise exact
claiming months, birth-cohort FRA, early reduction and delayed credits determine
it. Delayed credits earned in a midyear claiming year enter the benefit the
following January, or upon reaching 70. A January 1 birth belongs to the previous
attainment cohort. Retirement commencement must satisfy SSA's full-month age-62
rule.

For example:

```python
from policyengine_us import Simulation

simulation = Simulation(
    situation={
        "people": {
            "worker": {
                "ss_calculator_source": "aime",
                "ss_calculator_worker_id": "worker-record-1",
                "ss_calculator_birth_date": "1961-01-02",
                "ss_calculator_eligibility_year": 2023,
                "ss_calculator_entitlement_month": "2023-01",
                "ss_calculator_supplied_aime": 3000,
                "ss_calculator_insured": True,
                "ss_calculator_no_special_monthly_test": True,
                "ss_calculator_no_prior_withholding_adjustment": True,
                "ss_calculator_earnings_test_no_trigger": True,
            }
        },
    }
)
# SSA's 2023 example: $1,606.70 PIA, claim at 62/FRA 67 => $1,124.
monthly = simulation.calculate("ss_calculated_benefit", "2023-01")
checks = simulation.calculate("ss_calculated_annual_payment", 2023)
```

`ss_calculated_benefit` is the payable amount for an **entitlement month**;
`ss_calculated_payment` is cash paid in the requested month, including any
supplied earnings-test settlement. Ordinary checks follow entitlement by one
month, subject to whole-month earnings-test withholding.
`ss_calculated_annual_entitlement` sums January–December entitlement, whereas
`ss_calculated_annual_payment` sums checks actually paid January–December.
`ss_calculated_retirement` and `ss_calculated_survivors` expose the latter by
selected component. A first entitlement in July normally yields five checks
in that calendar year. COLAs effective December first affect January checks.
S.770 section 2(c)(1) first affects January 2026 benefit entitlement, normally
paid in February. Dated custom payment-year paths use the check year.

The pure `calculate_year` service returns both totals and a monthly ledger:
eligibility PIA, PIA after each COLA, exact claiming factor, unrounded benefit,
rounded gross benefit, capped earnings-test reduction and payable amount.
The engine also exposes monthly `ss_calculated_eligibility_pia`, annual
`ss_calculated_earnings_test_reduction`, and inferred PIA/AIME interval endpoints.
An absent inference interval is exposed as zero; the source selector identifies
which diagnostic applies.

## Earnings test and scope assertions

Supply annual `ss_calculator_annual_earnings`. In the FRA year supply
`ss_calculator_pre_fra_earnings`: only earnings before the retirement FRA month
count. No earnings test applies from FRA onward. Annual excess-earnings
deductions are truncated to whole dollars, allocated to the earliest affected
benefit months and capped at their benefits. Calculating January's check may
also require the previous year's earnings. A `-1` earnings input means missing,
not zero. Each annual earnings record must be supplied for its exact year;
an earlier record never carries forward. Alternatively assert `ss_calculator_earnings_test_no_trigger`; supplied
excess earnings contradicting it fail.

The default cash schedule withholds whole months, including the month whose
deduction leaves a partial entitlement. That remainder is deferred until
closed-year earnings reporting. [SSA Handbook §1806.2](https://www.ssa.gov/OP_Home/handbook/handbook.18/handbook-1806.html)
says, “The partial payment is paid only at the close of the taxable year”,
“unless otherwise requested”. [POMS RS 02501.110](https://secure.ssa.gov/poms.nsf/lnx/0302501110)
says, “Once we receive the closed-year earnings, pay a partial monthly benefit, if due.”

`ss_calculated_deferred_earnings_test_payment` reports the remainder deferred
from this entitlement year. Supply `ss_calculator_earnings_test_settlement_month`
for the **original earnings year**, with its actual later `YYYY-MM` payment
month, to include settlement in that month's and year's cash totals. A date
in or before the earnings year fails. Without a supplied date, the settlement
remains pending; the calculator does not assume when earnings are reported.
Settlement never changes the original entitlement or earnings-test deduction.

Set `ss_calculator_immediate_earnings_test_payment` to true only when immediate
partial payment was requested; it defaults false. The pure `calculate_year`
API exposes the same choice as `immediate_earnings_test_payment` and accepts
an earnings-year-to-month `earnings_test_settlement_months` mapping. Ledger
rows retain `payable_benefit` as entitlement and expose `payment_amount` after
deferral; dated settlement payments appear separately in `AnnualBenefit.settlements`.
For January 2026 commencement, $800 monthly benefits and $33,400 earnings,
the deduction is $4,460 and annual entitlement $5,140. Default 2026 checks total
$4,000 with $340 deferred; requested immediate partial payment gives $4,340.

This route requires `ss_calculator_no_special_monthly_test` and
`ss_calculator_no_prior_withholding_adjustment`. These assert that special
first-year monthly/service rules and actuarial adjustments for prior withheld
months do not affect the supplied case. Such cases need a separate computation
or a supplied authoritative claiming factor and a valid scope assertion; this
calculator does not silently approximate those rules. All entitlement before
commencement, or on an uninsured record, is zero.

The earnings-test implementation covers entitlement years from 2000 onward.
Earlier years require the explicit no-trigger assertion because historical
age limits and deduction rates differ. Positive benefits below one dollar
before December 2006 fail explicitly: their manual year-end payment timing
is outside the recurring monthly ledger. Later sub-dollar benefits retain
their dimes under SSA's payment-rounding exception.

## Restricted survivor

Select `survivor` and supply monthly gross paid amount, source valuation check
month, positive decimal-string composite ratio and a description of everything
that ratio includes. The ratio includes the case's survivor reduction and any
worker delayed credits, so no further claiming factor may be supplied.
Assert nonbinding RIB-LIM/family maximum, no dual entitlement, no earnings-test
withholding in the source valuation, and ordinary non-WINDEX scope.

The `ss_calculator_worker_birth_year`, `death_year`, optional exact worker birth
and death dates, optional `authoritative_year`, and `basis_provenance` identify
the computation benchmark. Every survivor record must explicitly supply
`ss_calculator_prior_disability_eligibility`: 1 means the worker initially
became eligible through disability before death; 0 means no prior eligibility.
The default -1 means unspecified and raises `ValueError`, as does any other
value. The pure `SurvivorBasis` input is `prior_disability_eligibility`, with
`True`/`False` for the same answers and `None` meaning unspecified.
Prior eligibility requires an authoritative computation basis. With no prior
eligibility, derive E as the earlier of death and age-62 attainment unless an
authoritative basis is supplied.
January 1 attainment uses the preceding year. A year-only fallback requires
`year_only_not_january_1`; death and age-62 attainment in the same year require
exact dates or `same_year_death_before_62` (1/0; -1 means unspecified).

COLAs begin with December of the accepted computation benchmark, paid the
following January. For a pre-62 death without prior eligibility, this is the
death benchmark. Recovery propagates the supplied final-payment interval
backward through the composite ratio and **every rounded COLA**, retaining a
half-open eligibility-PIA interval. The lower admissible dime is the point
convention; baseline forward computation must reproduce the supplied payment.
When reform needs AIME, invert the fixed unreformed PIA scale at that lower
endpoint and expose the corresponding AIME interval. Zero stays zero.

The default-false parameter
`gov.contrib.congress.s770.section_2.recompute_pre2026_death_before_eligibility`
controls only the 18% first-bend-point increase for pre-2026 deaths before any
initial eligibility. This requires both death before age 62 and the
explicit answer `ss_calculator_prior_disability_eligibility=0`. The 95% first
factor still applies when false.
An accepted authoritative prior-disability benchmark receives both changes
regardless of the switch, as do deaths in 2026 or later. S.770 section 2(c)(2)(B) includes
initial disability eligibility before 2026. See [the recorded modeling
ruling](social-security/RULINGS.md) and [the bill
text](https://www.congress.gov/bill/119th-congress/senate-bill/770/text).

## Shared PIA paths and policies

`tools.social_security.pia.compute_pia` is the common pure monthly service for
supplied AIME, recovered AIME and future history callers. Its inputs explicitly
separate initial eligibility, formula path, scoring/payment year and cohort vs
retroactive applicability. All computations and inverses require E >= 1983.
Historical bends back to 1979 are separate parameters, preserving legacy scale
values. Future bends use the model's existing wage-indexed projections.

`gov.contrib.ssa.pia` contains neutral bend-point multipliers, factors and cohort
start, an `in_effect` opt-in gate, and explicit `recompute_existing`. No top-factor package schedule is
selected. S.770 is separately enabled with
`gov.contrib.congress.s770.section_2.in_effect` and uses original eligibility
bend points for older beneficiaries.

Full price indexing requires a frozen cohort `real_wage_scale` path: cumulative
price growth divided by cumulative wage growth from the declared anchor. This
scales **all** formula factors. Progressive indexing requires a frozen
maximum-career AIME and PIA target, plus either `bend_point_fraction` or optional
`threshold` dollar path under `gov.contrib.ssa.pia.progressive_price_indexing`.
The dollar path overrides the fraction. Otherwise the protected threshold is
BP1(E) + f * (BP2(E) - BP1(E)). There is no default fraction. Enabling a path
without its required frozen inputs fails. Frozen scales, dollar thresholds,
maximum AIMEs and targets require explicit January observations for each
eligibility cohort; they never silently carry a prior cohort's data forward.
The policy fraction and ordinary factor schedules retain normal dated-policy
semantics. Both indexing paths also require their own `in_effect` switch and
start cohort; setting a fraction alone does not activate progressive indexing.
Ordinary settings read the eligibility-year snapshot. Explicit older-cohort
recomputation reads payment-year settings while retaining original-cohort
bend points and frozen indexing inputs. No population percentile or solvency
estimate supplies missing values. Scoring must pin price/wage bases, lags,
anchor, maximum-taxable career, source hashes and combined-policy order.
Composition order is custom bends/factors, S.770, full indexing, progressive
protected/maximum-target construction, and final eligibility dime truncation.

`gov.contrib.ssa.benefit_levers.cola.pp_change`,
`across_the_board.rate`/`start_year` and `payable.share` are the shared neutral
payment-year parameters reused from #10400. COLA settings also accept an
effective year/month, payment start/end year and a supplied alternative rate. The annual person
input `ss_calculator_withhold_cola` accepts an externally resolved E3 decision
when `cola.withholding_enabled` is true.
Each withholding decision applies only in its supplied year; an absent year's
decision is false.
Withholding sets that event's COLA to zero, jointly with any rate change; no
second COLA factor is applied. Payable shares must lie in [0,1], and rates must
not imply a negative benefit. A depletion-year midyear blend is supplied in the
annual payable-share path. E2 and E3 income/threshold computation belong to
their respective modules. The [COLA means test](../social-security-cola-means-test.md)
now supplies these decisions from prior-tax-year MAGI and filing status.

## Public source-selector wiring

The source selectors reuse the canonical COLA history and common lever
parameter files. Historical bend
points remain in a separate table because copying its legacy scale backfill
would change existing pre-2015 `ss_pia` outputs with this route disabled.
Select `social_security_retirement_source` as `supplied_aime` or `supplied_pia`
with matching `ss_calculator_source` of `aime` or `pia`. For the restricted
survivor route, select `social_security_survivors_source` as
`supplied_ratio_survivor` with calculator source `survivor`. The public benefit
then reads the calculated checks, bypassing population PIA, COLA, across-the-board
and payable factors already applied in this ledger. The earnings test runs
once. Explicit public final overrides retain their precedence. Calculated
checks are never written into `_reported` as original data.

## Sources and validation

Published fixtures cite [SSA Supplement 2023 Appendix D](https://www.ssa.gov/policy/docs/statcomps/supplement/2023/apnd.html),
[COLA application](https://www.ssa.gov/oact/COLA/colaapplic.html), and
[2026 earnings-test examples](https://www.ssa.gov/benefits/retirement/planner/whileworking.html).
Historical parameters cite [bend points](https://www.ssa.gov/OACT/COLA/bendpoints.html)
and [COLAs](https://www.ssa.gov/OACT/COLA/colaseries.html). December 1999 retains
its original 2.4% as-paid rate until the 2001 correction, then the corrected 2.5%
path; special one-time arrears are excluded from recurring gross benefits.
Earlier COLA rules are recorded, but E < 1983 routes fail explicitly.
