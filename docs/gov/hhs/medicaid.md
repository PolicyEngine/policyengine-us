# Medicaid

PolicyEngine determines Medicaid eligibility and enrollment for each person and gives each enrollee a dollar value, `medicaid`. The value is the enrollee's share of their state's total Medicaid spending. A cost index sets each enrollee's share. The index uses the Affordable Care Act (ACA) benchmark premium: the second-lowest-cost silver plan (SLCSP) premium for the enrollee's age and rating area or, in New York and Vermont, for their family tier. The value doesn't vary by eligibility group.

## Eligibility and enrollment

`medicaid_category` (`policyengine_us/variables/gov/hhs/medicaid/eligibility/categories/medicaid_category.py`) assigns each person the first coverage category they meet, in this order:

1. SSI recipient
2. Infant, young child or older child
3. Pregnant
4. Parent or caretaker relative
5. Young adult (ages 19-20)
6. Adult (the ACA expansion group)
7. Optional senior or disabled
8. Medically needy
9. Working disabled Buy-In
10. Section 1115 minimum essential coverage adult
11. Healthier Mississippi Waiver

42 CFR 435.119(b)(4) excludes people otherwise eligible for and enrolled in mandatory coverage. The model prioritizes mandatory categories before the adult expansion group.

`is_medicaid_eligible` (`policyengine_us/variables/gov/hhs/medicaid/eligibility/is_medicaid_eligible.py`) requires a category and an eligible immigration status. Where federal or Arkansas work requirements apply, it also requires the person to meet them. It also counts people eligible for California's Former Foster Youth Program (`ca_ffyp_eligible`), Illinois's Health Benefits for Immigrants (`il_hbi_eligible`) and Rhode Island's state-funded postpartum coverage (`ri_medicaid_state_funded_postpartum_eligible`).

`medicaid_enrolled` marks an eligible person as enrolled when `takes_up_medicaid_if_eligible` is true, except for Rhode Island postpartum enrollees who take up CHIP postpartum coverage. `takes_up_medicaid_if_eligible` is an input that defaults to true, so household calculations enroll every eligible person. In population runs, the microdata supply it.

## Value per enrollee

Three variables carry the value:

- `medicaid` adds `medicaid_cost`.
- `medicaid_cost` equals `medicaid_cost_if_enrolled` for people with `medicaid_enrolled` and 0 for everyone else.
- `medicaid_cost_if_enrolled` (`policyengine_us/variables/gov/hhs/medicaid/costs/medicaid_cost_if_enrolled.py`) computes the value for person $i$ in state $s$:

$$
\text{value}_i = S_s \times \frac{c_i}{D_s}
$$

where

- $S_s$ is the state's total Medicaid spending (`calibration.gov.hhs.medicaid.totals.spending`);
- $c_i$ is the person's cost index (`medicaid_slcsp_cost_index_filled`);
- $D_s$ is the state denominator (`medicaid_slcsp_state_denominator`).

The value is 0 when $D_s$ is 0.

### Cost index

`medicaid_slcsp_cost_index` reads the January SLCSP premium for the household's rating area, normalized to an enrollee aged 0 (`slcsp_age_0`). The [ACA page](aca.md) describes the rating areas, age curves and family tiers.

In every state except New York and Vermont, the index equals that premium times the ACA age-curve factor for the person's age in January (`slcsp_age_curve_multiplier`). Alabama, DC, Massachusetts, Minnesota, Mississippi, Oregon and Utah use their own curves, and the other 42 states use the federal default curve. From 2018, the default curve gives an enrollee aged 64 or older 3.92 times the index of a child under 15 in the same rating area.

New York and Vermont rate premiums by family tier. `medicaid_slcsp_family_tier_category` groups the Medicaid enrollees in each tax unit into one of these tiers:

| Tier | New York factor | Vermont factor |
|------|----------------:|---------------:|
| One adult | 1.00 | 1.00 |
| Two adults | 2.00 | 2.00 |
| One adult with one or more children | 1.70 | 1.93 |
| Two adults with one or more children | 2.85 | 2.81 |
| Children only | 0.412 | Age-rated |

`medicaid_slcsp_family_tier_multiplier` multiplies a New York tier factor by 1.05 when one of the tax unit's enrollees is a tax dependent aged 26 to 29. The parameter's first value is dated 2023-01-01; the model backfills that value to 2015. The multiplier then adds the one-adult factor for each enrolled adult beyond two. `medicaid_slcsp_family_tier_person_share` multiplies the age-0 premium by the factor and splits the result evenly among the tax unit's enrollees. `is_medicaid_slcsp_dependent_child` counts as a child anyone aged 20 or younger, a tax dependent under 26 and, in New York, a tax dependent aged 26 to 29. A Vermont tax unit whose only enrollees are children gets the age-rated index, which in Vermont equals the age-0 premium at every age.

Where the index is 0, `medicaid_slcsp_cost_index_filled` substitutes the state average (`medicaid_slcsp_state_average_cost_index`): the person-weighted mean of the positive indices among the simulation's people in that state.

### State spending and enrollment

Two parameter files under `policyengine_us/parameters/calibration/gov/hhs/medicaid/totals/` supply the state totals:

- `spending.yaml` holds total Medicaid spending in each state for federal fiscal years 2020 to 2024. The file cites KFF for fiscal years 2020, 2023 and 2024 and MACPAC for fiscal years 2021 and 2022.
- `enrollment.yaml` stores January Medicaid and CHIP enrollment inputs sourced from KFF for 2020 to 2024. North Carolina's 2020 to 2023 inputs are known not to match KFF's January counts.

Each January 1 entry pairs that federal fiscal year's spending with that year's enrollment input. The table below sums the model inputs, including the historical North Carolina discrepancy. Years after 2024 reuse the 2024 pair with no growth factor.

| Year | Spending, all states | Enrollment, all states |
|------|---------------------:|-----------------------:|
| 2020 | $661.5 billion | 71.4 million |
| 2021 | $744.5 billion | 80.8 million |
| 2022 | $818.3 billion | 87.2 million |
| 2023 | $880.0 billion | 93.3 million |
| 2024 and later | $918.7 billion | 84.9 million |

### State denominator

`medicaid_slcsp_state_denominator` computes $D_s$ in one of two ways.

**Population runs.** Over a dataset, $D_s$ sums person weight times cost index over the state's Medicaid enrollees. The weighted values of a state's enrollees then add up to $S_s$. A reform simulation keeps the baseline denominator but recomputes cost indices. In New York and Vermont, enrolling another family member can reduce existing enrollees' shares of a fixed tier premium, so additional enrollment need not raise total spending.

**Household calculations.** A household calculation has no population to sum, so $D_s$ equals the state's January enrollment times the state average index. For a single household, the state average index covers the household's own members. A lone enrollee therefore receives the state's spending divided by its enrollment. When every member of a household enrolls, their values average that amount and differ in proportion to their indices.

| State | FY2024 spending | January 2024 enrollment | Lone enrollee, 2024 and later |
|-------|----------------:|------------------------:|------------------------------:|
| California | $150,413,664,949 | 13,836,944 | $10,870.44 |
| New Jersey | $23,426,076,809 | 2,030,400 | $11,537.67 |
| New York | $96,024,580,523 | 7,115,535 | $13,495.06 |
| Texas | $50,974,507,372 | 4,295,157 | $11,867.90 |

Across the 50 states and DC, the lone-enrollee value for 2024 and later ranges from $6,673.73 in Hawaii to $14,975.49 in DC, with a median of $10,983.60.

### Federal and state shares

`medicaid_federal_cost` multiplies `medicaid_cost` by `medicaid_federal_share`, and `medicaid_state_cost` takes the remainder. `medicaid_federal_share` applies the expansion FMAP (`gov.hhs.medicaid.cost_share.expansion_fmap`, 42 U.S.C. 1396d(y)) to the adult expansion category and the state's regular FMAP (`gov.hhs.medicaid.cost_share.fmap`, 42 U.S.C. 1396d(b)) to every other category. It applies 0 to people with no category. It also applies 0 to Rhode Island state-funded postpartum enrollees unless they have a category and an eligible immigration status.

### Net income

`household_health_benefits` lists `medicaid_cost`, so Medicaid counts toward `household_benefits` and net income only when `gov.simulation.include_health_benefits_in_net_income` is true. That parameter defaults to false.

## Eligibility-group files

`medicaid_group` maps `medicaid_category` to five spending groups: child, non-expansion adult, expansion adult, aged or disabled, and none. No formula reads `medicaid_group`.

MACPAC eligibility-group files sit under `policyengine_us/parameters/calibration/gov/hhs/medicaid/`: spending in `spending/by_eligibility_group/` and enrollment in `enrollment/`. Their values are dated 2022, except expansion-adult spending, which is dated 2023. Only Oregon's and Washington's programs read them:

- `or_healthier_oregon_cost_if_enrolled` divides Oregon's group spending by its group enrollment. Where a group's enrollment is 0, it uses the national per-enrollee amount for that group in `totals/per_capita.yaml`.
- `wa_apple_health_cost_if_enrolled` divides Washington's child and expansion-adult spending by the matching enrollment.

## Known limits

- The cost index varies only by age, rating area and, in New York and Vermont, family tier. It has no term for disability or for other coverage. For a given age and rating area, and the same enrolled family composition in New York and Vermont, the index is unchanged by whether someone qualifies through SSI or the adult expansion group or also has employer coverage.
- No age curve rises after age 64. An enrollee aged 90 gets the same index as one aged 64 in the same rating area.
- Household calculations divide spending that covers Medicaid only by enrollment counts that include CHIP enrollees.
- Spending and enrollment for 2025 and later repeat the fiscal year 2024 and January 2024 values, so state totals don't grow after 2024.
- The MACPAC eligibility-group files affect only Oregon's and Washington's programs.

## References

1. KFF. [Total Medicaid Spending, FY 2024](https://web.archive.org/web/20261104084733/https://www.kff.org/medicaid/state-indicator/total-medicaid-spending/?currentTimeframe=0&sortModel=%7B%22colId%22%3A%22Location%22%2C%22sort%22%3A%22asc%22%7D). Archived November 4, 2026.
2. KFF. [Medicaid and CHIP Monthly Enrollment, January 2024](https://web.archive.org/web/20261026192300/https://www.kff.org/medicaid/state-indicator/medicaid-and-chip-monthly-enrollment/). Archived October 26, 2026.
3. 42 CFR 435.119. [Coverage for individuals age 19 or older and under age 65 at or below 133 percent FPL](https://www.ecfr.gov/current/title-42/section-435.119).
4. 42 U.S.C. 1396d. [Definitions](https://www.law.cornell.edu/uscode/text/42/1396d).

`spending.yaml` and `enrollment.yaml` cite the source for each earlier year.
