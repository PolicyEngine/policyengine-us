# SSI Spousal Deeming

This module implements the Supplemental Security Income (SSI) spousal deeming rules as specified in [20 CFR §416.1163](https://www.ssa.gov/OP_Home/cfr20/416/416-1163.htm).

## Overview

When an SSI-eligible individual lives with an ineligible spouse, a portion of the ineligible spouse's income may be "deemed" available to meet the needs of the eligible individual. This process is called spousal deeming.

## Deeming Process

The implementation follows these steps according to the regulations:

1. **Determine ineligible spouse's income** (§416.1163(a))

   - Calculate the ineligible spouse's earned and unearned income
   - Apply appropriate exclusions

2. **Apply allocations for ineligible children** (§416.1163(b))

   - Deduct allocations for ineligible children from the ineligible spouse's income
   - Deductions are made from unearned income first, then earned income
   - An ineligible child is the claimant's or the spouse's child who lives in the claimant's household and is not eligible for SSI (§416.1160(d)), and who is a child under §416.1856: under 18, or a student under the deeming age limit (under 21 before June 16, 2008, under 22 afterward); unmarried even when a legal spouse lives elsewhere; not the head of a household
   - `ssi_spousal_deeming_child_allocations` sums the allocations. Parent ids (`parent_1_id`, `parent_2_id`) decide whose child someone is. Without ids, the co-resident members of the claimant's or the spouse's tax unit stand in, as the parent-link contract in `household/demographic/person/_parent_links.py` allows; that proxy cannot tell a grandchild from a child
   - No allocation is made for a child receiving public income-maintenance payments (`ssi_receives_public_income_maintenance`)
   - Student earnings use the monthly student exclusion until its annual cap is exhausted. Each month retains its allocation through spouse-income deductions, the deeming threshold, income exclusions, floors and benefit caps; annual outputs sum the completed monthly calculations. Annual income inputs are spread evenly over the year
   - Existing income and allocation variables retain their annual input and output basis, including when supplied in a monthly situation. Their `*_monthly` counterparts carry each month's budget through the calculation chain and honor supplied annual inputs. Annual eligibility screens read the annual variables directly, avoiding rounding from dividing supplied annual income and summing it again
   - `is_ssi_spousal_deeming_applies` also retains its annual input basis; its calculated annual output remains the December status. Benefit calculations use `is_ssi_spousal_deeming_applies_monthly` for the current month's threshold
   - Parent deeming and its Medicaid counterpart also restrict allocations to relevant co-resident children. SSI recipient division uses SSI immigration status; Medicaid uses its own immigration eligibility and excludes its recipients from the allocation pool

3. **Compare remaining income to FBR differential** (§416.1163(d))

   - Compare the remaining income to the difference between couple and individual FBR
   - If no more than the differential, no income is deemed
   - If more than the differential, continue with deeming calculations

4. **Calculate combined countable income** (§416.1163(d)(2))

   - Combine the eligible individual's and ineligible spouse's incomes
   - Apply all appropriate income exclusions to the combined income

5. **Calculate deemed income amount**
   - The deemed amount is the difference between the combined countable income and the individual's countable income

## Exclusions Applied

Income exclusions are applied in the following order:

1. General exclusion ($20/month)
2. Earned income exclusion ($65/month)
3. 50% remainder reduction on earned income

## Testing

### Unit Tests

Unit tests for this variable directly test the `ssi_income_deemed_from_ineligible_spouse` calculation with various input scenarios:

- Disabled individual with working ineligible spouse
- Disabled individual with non-working ineligible spouse
- High-income scenarios
- Mixed income (earned and unearned) scenarios
- Income below FBR differential threshold

These tests can be found in `ssi_income_deemed_from_ineligible_spouse.yaml` and focus solely on testing this variable's specific logic.

### Integration Tests

Integration tests verify the full SSI benefit calculation pipeline and can be found in the `integration_tests.yaml` file. These tests check:

- The entire SSI benefit calculation for households with ineligible spouses
- Interactions between spousal deeming and other components of the SSI program
- Edge cases like income just below and above threshold values
- Households with various income combinations

Integration tests are particularly important for SSI spousal deeming as they validate the correct application of the regulation's multi-step process in a full benefit calculation context.

Monthly policy assertions and consumers must use the `*_monthly` variables. The existing annual public variables aggregate those monthly budgets; Core divides an annual variable by 12 when it is requested for a month, so that request is an annual average rather than the month’s budget.
