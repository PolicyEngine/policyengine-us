# OASDI modeled liabilities and benefits

Six outputs report modeled OASDI liabilities, modeled OASDI benefits and their
difference, the modeled balance. They add up existing variables and change no
other output. The balance compares modeled liabilities with modeled benefits;
it is not a trust-fund cash balance.

## Definitions

| Output | Entity | Definition |
| --- | --- | --- |
| `oasdi_payroll_tax_revenue` | Person | `employee_social_security_tax + employer_social_security_tax + self_employment_social_security_tax` |
| `oasdi_benefit_taxation_revenue` | TaxUnit | `tob_revenue_oasdi` |
| `oasdi_niit_revenue` | TaxUnit | `s770_revenue_oasdi` |
| `oasdi_income` | Household | Each member's `oasdi_payroll_tax_revenue`, plus each tax unit's `oasdi_benefit_taxation_revenue` and `oasdi_niit_revenue`, each counted once |
| `oasdi_cost` | Household | Members' public `social_security`, after any enabled benefit policies |
| `oasdi_modeled_balance` | Household | `oasdi_income - oasdi_cost` |

The payroll leaves read their rates and the wage base from parameters:
`gov.irs.payroll.social_security.rate.employee` and `.employer` apply to wages
up to `gov.irs.payroll.social_security.cap`, and
`gov.irs.self_employment.rate.social_security` applies to self-employment net
earnings in the room that wages leave under the base. A reform that replaces a
leaf reaches the sum through that leaf. The owners' draw reform's
`self_employment_social_security_tax` adds `owners_draw_oasdi_tax`, so the draw's
OASDI tax counts once; don't add it again.

`oasdi_benefit_taxation_revenue` is the OASDI share of income tax on benefits:
the tax with section 86 inclusion as before the 1993 amendments, less the tax
with no inclusion. The HI share, `tob_revenue_medicare_hi`, stays out. The share
carries a sign: a unit whose tax falls when its benefits enter income contributes
a negative amount, so sum units without a floor.

`oasdi_niit_revenue` is the OASDI transfer that the enabled S.770 section 8
options select. It is zero unless an option applies, and it counts only the
transfer, not the whole `net_investment_income_tax` liability. See the
[S.770 section 8 README](https://github.com/PolicyEngine/policyengine-us/blob/main/policyengine_us/reforms/congress/s770/README.md)
for the transfer modes.

### Flows left out

* `employer_total_social_security_tax` applies the employer rate to
  `employer_total_taxable_earnings_for_social_security`, a separate input for
  employer-only payroll tax calculations that defaults to zero, rather than to a
  worker's own wages. Where both are populated they describe the same employer
  liability, so the sum keeps only the worker-level `employer_social_security_tax`
  and the aggregate is not a fourth stream.
* `unreported_payroll_tax`, the tax on unreported tips and wages from Forms 4137
  and 8919, is a TaxUnit input that doesn't separate OASDI from HI.
* `employer_ss_tax_income_tax_revenue`, the income tax on employer OASDI
  contributions under the contributed reform that counts employer payroll tax as
  income, isn't part of `oasdi_income`. A score that enables that reform adds it
  separately.

### Benefit taxation and the NIIT transfer overlap

`tob_revenue_oasdi` takes the difference in `income_tax`, which includes
`net_investment_income_tax`. Including benefits raises adjusted gross income and
so `niit_magi`, so any NIIT that benefit inclusion triggers lands in the benefit
taxation term. The trust fund transfer covers only chapter 1 income tax
liabilities, and the NIIT sits in chapter 2A, so that piece doesn't belong in
the term even at baseline. With an S.770 section 8 option on, `oasdi_niit_revenue`
also transfers a share of the whole resulting NIIT, so `oasdi_income` counts the
NIIT that benefit inclusion triggers in both terms. The fix belongs in
`tob_revenue_oasdi`, which these outputs read unchanged. Until it lands, treat
`oasdi_income` as overstated for beneficiaries whose inclusion pushes them past
the NIIT threshold under section 8.

## Entity mapping and weights

`oasdi_income` credits each tax unit's amount once, to the household of its
first member. `Microsimulation` weights a tax unit by that same household's
weight, so household-weighted totals equal the Person and TaxUnit weighted
totals. PE-US declares that tax units sit inside households, and the chunked
helper below requires it. If data ever breaks that nesting, the first-member
credit still keeps the weighted totals equal. Core's group-to-group `adds` would
instead split a tax unit's amount equally among its members and credit each
member's share to that member's household.

When you aggregate, sum each output at its own entity with that entity's
weights, once. Don't project a tax-unit amount to its members and sum it again:
`calculate("oasdi_benefit_taxation_revenue", map_to="person").sum()` counts a
married couple's amount twice.

## Stated limitations

This page states these limitations without measuring them. No residual from
another model closes them.

**Missing cash flows.** The modeled balance leaves out interest on trust fund
reserves, the Railroad Retirement financial interchange, administrative
expenses and general-fund reimbursements. None of these flows is a model
variable.

**Recipients outside the frame.** `oasdi_cost` sums benefits for the people in
the household dataset. The dataset misses or only partly represents
beneficiaries outside its frame, such as those living abroad.

**Noncovered employment.** `payroll_tax_gross_wages` is employment income less
FICA pre-tax contributions, with no general OASDI-coverage flag. The model
therefore taxes wages from employment that OASDI doesn't cover, such as some
state and local government jobs, as covered wages. This wage-coverage
assumption differs from the missing cash flows.

**Pass-through classification in the scoring data.** The owners' draw term in
payroll liability and the active-business part of `oasdi_niit_revenue` depend on
pass-through classification fields. The certified artifact's stored columns
don't include `passive_partnership_s_corp_income`, which therefore defaults to
zero. Population values for those two terms stay provisional until a scoring
artifact carries the repaired fields and the preflight receipt confirms them;
the [S.770 section 8 README](https://github.com/PolicyEngine/policyengine-us/blob/main/policyengine_us/reforms/congress/s770/README.md#scoring-data-limitation)
describes the repairs.

## Scoring a population

1. **Audit the stored data first.** Run the
   [scoring-data preflight](social-security-scoring-preflight.md) on the exact
   H5 you'll score:

   ```bash
   python -m policyengine_us.tools.social_security_preflight /data/populace_us_2024.h5 > receipt.json
   ```

   It checks the artifact's hash and base year and the four benefit components'
   sources. It also rejects stored columns that would bypass these formulas: the
   six outputs above, aggregate `social_security`, the worker and employer OASDI
   tax leaves, the TOB revenue leaves, and the NIIT liability and transfer
   leaves, including the S.770 section 8 and owners' draw tax and OASDI
   transfer leaves. Keep the receipt with the score.

2. **Score in household chunks.** On main, `tob_revenue_oasdi` recalculates
   income tax in two branches of the whole simulation, so its working memory
   grows with the population. Household-chunked calculation,
   [PolicyEngine/policyengine-us#10561](https://github.com/PolicyEngine/policyengine-us/pull/10561),
   is the supported route for full-population scoring once it merges. Review
   may still change its interface, so check its documentation when it lands.
   Score the same file the preflight hashed. With the interface under review, a
   call looks like this:

   ```python
   from policyengine_us import Microsimulation
   from policyengine_us.tools.calculate_chunked import calculate_chunked

   result = calculate_chunked(
       lambda dataset: Microsimulation(dataset=dataset, dataset_end_year=2035),
       [
           "oasdi_payroll_tax_revenue",
           "oasdi_benefit_taxation_revenue",
           "oasdi_niit_revenue",
           "oasdi_income",
           "oasdi_cost",
           "oasdi_modeled_balance",
       ],
       2030,
       8,
       dataset="/data/populace_us_2024.h5",
   )
   totals = result.weighted_sums
   ```

   The helper keeps households whole and requires each tax unit to sit inside
   one household, so each output's chunk totals add to its population total.

3. **Check the identities on the totals.** The `oasdi_income` total equals the
   payroll, benefit-taxation and NIIT-transfer totals added together, and the
   `oasdi_modeled_balance` total equals the `oasdi_income` total less the
   `oasdi_cost` total.

4. **Treat projected years as independent cross-sections.** The preflight guide
   describes how `extend_single_year_dataset` projects each year from the base
   year. Report the limitations above with every score.
