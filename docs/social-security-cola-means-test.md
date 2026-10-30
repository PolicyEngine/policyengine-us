# Social Security COLA means test

The contributed COLA means test is disabled under current law. It can withhold
an annual COLA based on the beneficiary's tax unit, while retaining the benefit
level reached before that event. It supports both reported benefit components
and the supplied-record household calculator. Scenario thresholds and dates
come from the scoring settings; PE-US does not choose package values.

## Policy basis and choices

The income test follows [OACT provision A9 on the 2026 Trustees Report
basis](https://www.ssa.gov/OACT/solvency/provisions/cola.html). Its instruction
is: “Use prior tax year income data for this determination.” The live page
was available when this implementation was prepared.

A9 uses a chained CPI-U COLA below the income line and no COLA above it, for
all beneficiaries beginning with the December 2028 COLA. Its single,
head-of-household and separate filers share a line; joint filers have twice
that line. It also specifies chained CPI-U before benefit receipt. Its example
lines are $85,000 and $170,000 in 2018 dollars, indexed by CPI-U. The preset
below implements these mechanics. Its 2029 income lines are $117,800 single
and $235,700 joint. OACT's displayed December 2028 lines of $117,300 and
$234,600 use a different CPI projection; this model uses the authored CPI-U
path described below.

The default enabled scenario differs from A9 in two parameterized ways: it
retains the statutory COLA below the line and restricts the policy to people
first eligible from 2026. The effective date, first-eligible year, filing-group
mapping, dollar lines, base year, index lag and rounding increment are also
parameters. A surviving spouse maps to the joint line by default; this is a
modeling choice because A9 does not name that status. Only income strictly
above the line withholds a COLA. Equality receives the COLA, an explicit
convention for A9's otherwise unspecified equality case.

## Parameters and activation

All paths in this table are relative to
`gov.contrib.ssa.benefit_levers.cola.means_test`.
Choice parameters use numeric codes because the parameter engine does not
accept string-valued choices. The semantic names below label those codes;
reforms must supply the numbers.

| Parameter | Current-law/default value | Scenario meaning |
| --- | --- | --- |
| `enabled` | `false` | Opt into the means test. |
| `scope` | `0` = `first_eligible_cohorts` | Alternatively, `1` = `all_beneficiaries`. |
| `first_eligible_year` | `2026` | Inclusive first-eligibility boundary in cohort mode. |
| `effective_year`, `effective_month` | `2026`, `12` | First affected effective COLA; ordinarily first paid January 2027. |
| `below_threshold_cola_index` | `0` = `statutory` | Alternatively, `1` = `chained_cpi_u`. |
| `pre_receipt_cola_index` | `-1` = `follow_below_threshold` | Follow the below-line choice, or explicitly select `0` = `statutory` or `1` = `chained_cpi_u`. |
| `income_sensitivity` | `0` = `prior_year` | Alternatively, `1` = `never_withheld` or `2` = `always_withheld`. |
| `thresholds.base_year` | `2026` | Dollar year of the supplied lines. |
| `thresholds.single`, `thresholds.joint` | `0`, `0` | Neutral placeholders; evaluated `prior_year` income decisions require positive scenario lines. |
| `thresholds.index_lag` | `1` | Years before the payment year for the December 1 CPI-U lookup. |
| `thresholds.rounding` | `100` | Dollar increment, rounded half up. |
| `filing_groups.SINGLE` | `0` = `single` | Select the single line; `1` selects joint. |
| `filing_groups.HEAD_OF_HOUSEHOLD` | `0` = `single` | Select the single line; `1` selects joint. |
| `filing_groups.SEPARATE` | `0` = `single` | Select the single line; `1` selects joint. |
| `filing_groups.JOINT` | `1` = `joint` | Select the joint line; `0` selects single. |
| `filing_groups.SURVIVING_SPOUSE` | `1` = `joint` | Modeling choice; `0` selects single. |

`means_test.enabled` activates both the income decision and the selected index
without requiring another switch. The enclosing `cola.withholding_enabled`
remains the A5 switch for externally resolved withholding decisions when the
means test is disabled. With the means test enabled, use the separate annual
Person inputs `social_security_X_cola_override` and
`ss_calculator_cola_override`: `-1` means automatic (the default), `0` means
paid, and `1` means withheld. Each person's default remains automatic when
another person supplies an override. The automatic timing, cohort and receipt
restrictions apply to automatic decisions; an explicit override supplies the
final decision for that person and year. The tri-state overrides expire after
their supplied year; later years return to automatic decisions.

With the means test disabled, the reported route retains A5's boolean
`social_security_X_cola_withheld` inputs and their legacy carry-forward
behavior. The calculator reads only `ss_calculator_withhold_cola`, in its
explicitly supplied year. Component boolean inputs do not reach the
calculator. These legacy boolean channels do not override an enabled means
test; use the separate tri-state inputs for that purpose.

Positive single and joint lines are required when a `prior_year` income
decision is evaluated. The `never_withheld` and `always_withheld` sensitivities
and pre-receipt index-only events do not read those lines.

The `a9` preset in `policyengine_us.reforms.ssa.cola_means_test` enables the
policy and selects:

```yaml
scope: 1  # all_beneficiaries
effective_year: 2028
effective_month: 12
below_threshold_cola_index: 1  # chained_cpi_u
pre_receipt_cola_index: 1  # chained_cpi_u
income_sensitivity: 0  # prior_year
thresholds:
  base_year: 2018
  single: 85000
  joint: 170000
  index_lag: 1
  rounding: 100
```

Apply it as a reform, for example:

```python
from policyengine_us import Simulation
from policyengine_us.reforms.ssa.cola_means_test import a9

simulation = Simulation(situation=situation, reform=a9)
```

These are public A9 example settings, not a scenario's package values. The
first affected checks are in January 2029. The ordinary contributed scenario
instead supplies its own positive 2026-dollar lines and retains the default
statutory/cohort choices unless its policy specifies otherwise.

## Prior-year income and filing status

`social_security_cola_means_test_magi` is a dedicated annual TaxUnit variable.
Its definition is AGI less taxable Social Security, plus tax-exempt interest
and the IRMAA-style exclusions under Internal Revenue Code sections 135, 911,
931 and 933. AGI retains its applicable deductions. This implements the
required MAGI excluding Social Security, replacing the earlier gross-source
income proposal. The [A9-linked actuarial memorandum, provision 5 on page
8](https://www.ssa.gov/OACT/solvency/SJohnson_20161208.pdf) connects the lines
to Medicare IRMAA; [H.R. 6489 section
103(d)](https://www.congress.gov/bill/114th-congress/house-bill/6489/text)
supplies the corresponding IRMAA definition reference. Excluding Social
Security and using the prior year are requirements of this contributed lever.

For COLAs first paid in year `y`, the decision reads this MAGI and filing
status for tax year `y - 1`. It never substitutes current-year AGI. A supplied
MAGI history can directly set the dedicated variable for the relevant tax
years; supplied histories of its income sources and filing status also take
precedence over projected records. A tax unit's decision maps to each
beneficiary, subject to that component's exposure and cohort scope.
Core stores complete input arrays for each variable and period; an income
history column must supply a value for every tax unit in that array.

Although prior-year AGI can depend on prior-year Social Security, every
benefit-related lookback moves to an earlier year. The dependency chain stops
before the policy's first affected event. It cannot return to the same
benefit/year pair. Multi-year dependency-graph tests exercise this decreasing
year chain, including deductions whose MAGI depends on taxable benefits.
The household engine resolves decisions only through the requested check
year for payment outputs. It does not eagerly read the income for the next
January COLA while computing this year's checks. December entitlement and
annual entitlement can require that next event; their prior-income dependency
uses the separate public payment route.

Population scoring uses a **static-cross-section prior-income proxy**.
Dataset extension starts each year from the same original record and uprates
its monetary sources separately. The `y - 1` record is that same record's
extended prior-year copy, not an observed longitudinal income history. Ages,
cohorts and household composition are not carried forward as a person's
history. Supplied histories override this proxy. Compare
`income_sensitivity = 1` (`never_withheld`) and `2` (`always_withheld`) to
report the missing-income-history sensitivity envelope; both retain policy
timing and cohort scope.

## Threshold indexing and COLA construction

For filing group `g`, base year `b`, payment year `y`, index lag `L` and
rounding increment `R`, the income line is:

```text
line(g, y) = round_half_up_to_R(
    base_line(g) * CPI_U(December, y - L) / CPI_U(December, b)
)
withheld(y) = prior_year_MAGI > line(g, y)
```

The code reads `gov.bls.cpi.cpi_u` at December 1 of year `y - L`, and at
December 1 of the base year. Under the parameter lookup's ordinary semantics,
this returns a BLS December figure where one exists, otherwise the latest
authored value. The series currently contains BLS monthly observations
through June 2026, so `cpi_u("2026-12-01")` returns June 2026's `332.568`.
For later years it uses CBO's February-keyed projection: for example,
`cpi_u("2028-12-01")` returns `348.3`, authored at `2028-02-01`.
These reads do not construct a separate December projection series.

The default one-year lag uses the December 1, 2028 lookup for January 2029
checks. The A9 preset's $85,000/$170,000 base lines, December 2018 value
`251.233`, and projected value `348.3` give $117,800/$235,700 after nearest-$100
half-up rounding. OACT's displayed $117,300/$234,600 lines use a different
CPI projection. The December 1 lookup, one-year payment lag and rounding are
documented modeling conventions: A9 specifies CPI-U indexing without
prescribing these details. Pin both the authored index path and these
settings for a score.

The chained option uses Q3 averages of July, August and September levels from
`gov.bls.cpi.c_cpi_u`. As with the statutory CPI-W schedule, positive growth
is rounded half up to 0.1 percentage point; nonpositive or rounded-zero growth
gives no COLA. The comparison base is the Q3 associated with the last positive
index-derived COLA. A withheld year still advances that index schedule's
comparison base when its rounded rate is positive: income withholding must
not create a catch-up COLA later. Neither withholding nor a downward rate
adjustment reduces the nominal benefit level. Historical benefit-rounding
rules remain attached to their individual events.

Before receipt, `pre_receipt_cola_index` controls COLAs accrued since initial
eligibility. Its default follows `below_threshold_cola_index`; the A9 preset
therefore uses chained CPI-U for these events. From the policy's effective
start, these pre-receipt events use the chosen index without an income test.
Supply entitlement and worker eligibility dates when known. Missing-date
cohort and exposure approximations remain those described in the
[benefit-lever guide](social-security-benefit-levers.md), including
adjacent-cohort sensitivities for integer-age uncertainty.

An active A5 `cola.alternative_rate` overrides the index selected here. The
applicable `cola.pp_change` is then added to that rate, and the final rate is
floored at zero. Withholding overrides the entire resulting increase.

## One joint COLA adjustment

Each annual Person variable `social_security_X_cola_means_test_withheld`, for
`X` equal to `retirement`, `disability`, `survivors` or `dependents`, resolves
its tax unit's automatic decision and that person's separate
`social_security_X_cola_override` input. The legacy
`social_security_X_cola_withheld` boolean remains A5's input channel when the
means test is disabled.
For a reported benefit, the population adjustment accumulates one ratio for
each exposed event:

```text
event numerator = 1                         if withheld
                  1 + adjusted_COLA        otherwise
event ratio     = event numerator / (1 + statutory_COLA)
joint factor    = product of the exposed event ratios
```

The adjusted rate includes the selected index and applicable percentage-point
change, with a floor of zero. For example, statutory rates of 2% and 3% plus a
CPI-E-style addition of 0.15 percentage points give numerators `1.0215` and
`1.0315` if paid. If the second year is withheld, the two-year factor is
`(1.0215 / 1.02) * (1 / 1.03)`, approximately `0.97230`. The reformed level
from a pre-event amount of $1,000 is $1,021.50, compared with the statutory
$1,050.60. The withheld event receives no CPI-E increase. An independently
multiplied withholding factor would give the wrong result.

The household calculator applies the same per-year decisions inside its COLA
schedule. It rounds the resulting PIA under the applicable event rule and
applies claiming and payment calculations once. With the means test enabled,
the annual `ss_calculator_cola_override` takes precedence over the component
override, followed by the automatic decision. With the means test disabled,
it retains A5's exact-year `ss_calculator_withhold_cola` channel.

For a public retirement component, select `social_security_retirement_source`
as `supplied_aime` or `supplied_pia`, and supply the matching
`ss_calculator_source` of `aime` or `pia`. For a restricted survivor record,
select `social_security_survivors_source = supplied_ratio_survivor` and
`ss_calculator_source = survivor`. These routes retain the calculator's input
and scope requirements in the [calculator
guide](usage/social-security-calculator.md).

Calculated public routes bypass all population benefit factors: the engine
already applies the COLA, across-the-board and payable policies to its ledger.
Reported sources use the population factors. This avoids applying any of
these policies twice. Switching a policy off later does not restore an
earlier withheld increase.

## Validation contract

Validation covers all statutory/chained and cohort/all-beneficiary
combinations, both sides of the first-eligibility boundary, the A9 preset,
all filing statuses, equality, supplied histories, and both income
sensitivities. Boundary cases include a zero statutory COLA, negative rate
adjustments, high-water years and combined CPI-E changes and withholding.
Multi-year graph checks establish that the prior-year income read has no
cycle. Calculated-source cases check that the COLA policy is applied once.

Compatibility checks pin literal results from main for disabled-policy
reported and calculator routes, including A5 inputs. Other checks require
nonincreasing benefits when a year is withheld and monotone withholding as
income rises at a fixed line. Multi-person cases preserve each person's
automatic decision when someone else supplies an override. Differential
checks cover reported situations, downstream outputs and household
calculator examples with this means test disabled.
Population impact requires a separately pinned scoring run; these mechanics
do not substitute OACT's solvency estimates for a PE-US result.
