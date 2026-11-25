# Retirement, capital gain and lot-level income tax rules

These rules were added for portfolio simulations that compute 2026 individual
income tax. Every new input defaults to zero or false, so callers that omit
them get the same results as before.

## How results reach the tax calculation

| Result | Reaches the tax calculation |
|---|---|
| Early-distribution tax, missed-RMD excise | `form_5329_additional_taxes`, added beside `qualified_retirement_penalty` in federal tax (and in Iowa's federal tax deduction) |
| California 2.5% / 6% | `ca_early_distribution_additional_tax`, added to California tax before refundable credits |
| Long-term gains (60% of §1256, home sale gain, long-term lot results) | `long_term_capital_gain_adjustments`, part of `long_term_capital_gains` |
| Annuities, Simplified Method, LTC per diem | new federal gross income sources |
| Savings bond exclusion | formula for the existing `us_bonds_for_higher_ed` deduction |
| Short-term gains, dividend reclassification, bond interest | `apply_investment_lot_adjustments` (see below) |

`short_term_capital_gains`, the dividend inputs and `taxable_interest_income`
are plain inputs that datasets uprate, so a formula cannot add to them. Call
`policyengine_us.tools.investment_lots.apply_investment_lot_adjustments(situation, year)`
before `Simulation(situation=...)`; it computes `short_term_capital_gain_adjustments`,
`investment_lot_interest_adjustment`, `dividends_failing_qualified_holding_period`
and `section_199a_dividends_failing_holding_period` and folds them into those
inputs.

A caller that sets `long_term_capital_gains` directly replaces its formula,
including the adjustments; set `long_term_capital_gains_before_response`
instead. A caller that sets `qualified_retirement_penalty` should leave the
Form 5329 inputs empty.

## Rules

**Early distributions (IRC 72(t), 72(q); Form 5329 Part I).** 10% of early
plan and IRA distributions, 25% for SIMPLE IRA distributions in the first two
years, 10% of premature annuity distributions, less exceptions. The simulator
decides which exception applies; PolicyEngine applies the caps: first-time
homebuyer $10,000 lifetime, birth or adoption $5,000 per child, emergency
$1,000 a year, domestic abuse $10,500 (2026, Notice 2025-67), disaster
$22,000 per disaster, medical expenses above the AGI floor. Inputs:
`early_distributions_from_retirement_plans`,
`early_distributions_from_simple_ira_first_two_years`,
`early_distributions_from_annuity_contracts` and the `early_distribution_*`
exception fields. These are memo amounts already in the retirement income
inputs. `early_withdrawal_penalty` remains the CD penalty deduction only.

**California (R&TC 17085(c); FTB 3805P).** 2.5% of the federal base, and 6% of
the SIMPLE two-year base. `ca_early_distributions_not_excepted_in_california`
carries amounts California does not except (529-to-Roth, IRA-to-HSA,
qualified recovery assistance distributions).

**Required minimum distributions (IRC 401(a)(9), 4974).** Applicable age
73 for people born 1951–1959 and 75 from 1960 (IRC 401(a)(9)(C)(v)). The
divisor is the Uniform Lifetime Table (Treas. Reg. 1.401(a)(9)-9(c)) or an
override for the Joint and Last Survivor Table. QLACs are excluded if total
premiums are within $210,000 (2026). The first year can be deferred to
April 1, and the still-working exception applies to employer plans. IRA and
employer-plan shortfalls are measured separately. The excise is 25% of the
shortfall, or 10% if corrected timely, less any waiver. Beneficiary RMDs
come in as amounts (`rmd_inherited_*`).

**Section 1256 contracts.** `section_1256_net_gain` (Form 6781 line 7,
including year-end mark-to-market) is split 60% long-term and 40% short-term.

**Home sale (IRC 121).** $250,000 exclusion, or $500,000 for a married couple
when the spouse meets the use test. Other features:
- ownership and use of 24 of the last 60 months each;
- the two-year bar on a second exclusion;
- the reduced exclusion for job, health or unforeseen-circumstance moves;
- no exclusion for the nonqualified-use share or for depreciation after
  May 6, 1997.

The depreciation part should also go in
`unrecaptured_section_1250_gain_before_losses`.

**Savings bonds (IRC 135; Form 8815).** Interest × (qualified expenses ÷
proceeds), phased out over $101,800–$116,800 of modified AGI ($152,650–$182,650
joint) in 2026, and none on separate returns. Modified AGI leaves out taxable
Social Security, which PolicyEngine computes from an AGI that already includes
the exclusion. `savings_bond_education_exclusion_magi_override` supplies an
exact figure. Treasury parameters record the $10,000 annual purchase limit and
the 3-month interest forfeiture before 5 years. Interest deferral is the
simulator's choice of when to report interest. Excluded bond interest should
be removed from `us_govt_interest_person`, so states do not subtract it again.

**Long-term care per diem (IRC 7702B(d); Form 8853 Section C).** Per diem
benefits above the greater of $430 × days (2026) and actual costs, less
reimbursements, are taxable.

**Annuity contracts (IRC 72(b), (c), (e)).** Three slots per person,
`annuity_contract_<n>_*`:
- exclusion ratio of investment ÷ expected return;
- the exclusion stops once the investment is recovered, for starting dates
  after 1986;
- withdrawals are taxed income first, after any pre-August 14, 1982
  investment;
- partial annuitization splits the investment.

Contracts aggregated under IRC 72(e)(12) go in one slot. A 1035 exchange is
not a taxable event: carry the investment into the new slot. The Simplified
Method (IRC 72(d)) covers qualified-plan annuities with after-tax cost. Neither
may also be reported in `taxable_pension_income`.

**Lot-level rules.** Five slots of each kind per person. Sales and bond
gains entered here must be left out of the aggregate gain inputs. Dividend
lots describe dividends already in the dividend inputs.
- Qualified dividend holding period: more than 60 days in the 121-day window
  (90 days of 181 for long-period preferred). For section 199A REIT
  dividends, more than 45 days of 91. Days held must exclude hedged days.
- Wash sales (IRC 1091): substantially identical purchases within 30 days
  before or after a loss sale disallow the matching share of the loss. An
  IRA purchase disallows it permanently (Rev. Rul. 2008-5). The deferred
  amount (`wash_sale_disallowed_loss_deferred`) must be added to the
  replacement basis by the simulator.
- RIC shares held six months or less (IRC 852(b)(4)): the loss is disallowed
  up to exempt-interest dividends (not for daily-dividend funds), then is
  long-term up to capital gain dividends.
- Bonds: OID under the constant-yield method (zero if de minimis), reduced by
  any acquisition premium fraction; ratable market discount, as interest at
  sale or currently by election; and bond premium amortization under IRC 171.

## Not modeled

- **Federal 10% tax:** whether a distribution meets an exception is the
  simulator's decision; the domestic-abuse 50%-of-balance limit is also left
  to it.
- **California exceptions:** which SECURE Act exceptions California has
  adopted (birth or adoption, for example) is not certain; amounts California
  does not except go in the California-only input.
- **Required minimum distributions:**
  - beneficiary RMD computation;
  - the pre-2022 Uniform Lifetime Table (earlier years use the 2022 table);
  - 403(b) aggregation beyond one combined group.
- **Annuities:**
  - expected return from the Treas. Reg. 1.72-9 tables;
  - the deduction for unrecovered investment at death;
  - the IRC 72(s) distribution-at-death rules.
- **Bonds:**
  - constant-yield market discount;
  - premium amortization computation;
  - tax-exempt bond premium;
  - short-term obligations.
- **Lot rules:** straddles, constructive sales, and wash sales across spouses.
- **Not income tax (left out):**
  - state annuity premium taxes;
  - estate, inheritance and gift taxes;
  - crypto broker reporting;
  - withholding, MEC 7-pay and Table V;
  - product charges.
