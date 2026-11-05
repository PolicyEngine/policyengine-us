# State rebate attribution

PolicyEngine attributes one-time state rebates to the tax year whose return
determines eligibility and amount, even when checks arrive in a later
calendar year. Rebates included in state credit totals reduce
`state_income_tax` and increase household net income in that eligibility year.
This attribution convention does not describe the payment calendar. Some
standalone rebate formulas can calculate an amount after the rebate ends;
use the dated credit total to establish whether that amount enters tax or net
income. Do not add back every positive raw rebate column in every year.
Massachusetts premium pay is also modeled through state refundable credits.
A payment modeled solely as a benefit would affect household net income
without reducing state income tax.

For comparison, restore only the rebate amounts that actually reduced that
year's reported state tax, including liability limits on nonrefundable
credits. Ordinary recurring refundable credits remain part of liability.
`state_income_tax_before_refundable_credits` removes those ordinary credits
too, so it is not a pre-rebate liability measure. Colorado Cash Back and the
residual TABOR sales tax refund are separate mechanisms; count each only
through its stated aggregation path and eligibility year.

## Inventory

The years below are eligibility tax years in which a qualifying household can
receive a nonzero contribution to the state's credit total. `R` denotes the
state's refundable-credit total; `N` denotes its nonrefundable-credit total.
Every listed payment enters state tax through credits, including Colorado Cash
Back and Massachusetts premium pay. None is a second, direct household benefit
payment. Refundable totals enter both state tax and household refundable credits;
nonrefundable totals reduce tax before refundable credits.

| Rebate and variable(s) | Eligibility years included in state credit totals | Payment year | Aggregation and amount gate |
|---|---|---|---|
| Colorado residual TABOR sales tax refund: `co_sales_tax_refund`; helpers `co_sales_tax_refund_eligible`, `co_sales_tax_refund_person_eligible` | 2015, 2021–2025, and 2027 onward under current parameters; zero in 2016–2020 and 2026 | Following the eligibility return | R: `co_refundable_credits`. The formula multiplies the eligible-filer amount by `sales_tax_refund.in_effect`. This recurring residual mechanism is separate from Colorado Cash Back. |
| Colorado Cash Back: `co_tabor_cash_back` | 2021 only | 2022 | R: `co_refundable_credits`, removed from the dated list in 2022. The amount is zero outside 2021. |
| Illinois income and property rebates: `il_income_tax_rebate`, `il_property_tax_rebate`; helpers `il_income_tax_rebate_eligible`, `il_property_tax_rebate_eligible` | 2021 only | 2022 | R: `il_refundable_credits`, removed from the dated list in 2022. Income-rebate amounts and the property-rebate cap are zero before 2021. |
| New York inflation refund: `ny_inflation_refund_credit` | 2023 only | 2025 | R: `ny_refundable_credits`. The variable has a 2023 formula and resets to zero in 2024. |
| Virginia rebates: `va_rebate` | 2021, 2022, and 2024 | 2022, 2023, and 2025, respectively | N: `va_non_refundable_credits`, limited by available tax liability. Amounts are zero in other years. |
| Georgia surplus refund: `ga_surplus_tax_rebate` | 2021 only | Later than the eligibility return | R: `ga_refundable_credits`. The O.C.G.A. 48-7-20.2 refund is capped at income tax before credits; the amount is zero outside 2021. |
| Arizona Families Tax Rebate: `az_families_tax_rebate` | 2021 only | 2023 | R: `az_refundable_credits`. The dated list excludes it before 2021 and removes it in 2022, even when its standalone formula returns a positive amount. |
| New Mexico rebates: `nm_2021_income_rebate`, `nm_additional_2021_income_rebate`, `nm_supplemental_2021_income_rebate` | 2021 only | Enacted in 2022 and 2023 for the 2021 return | R: `nm_refundable_credits`, removed from the dated list in 2022. All filing-status amount branches are zero before 2021. The supplemental variable combines two payments. |
| Connecticut child rebate: `ct_child_tax_rebate` | 2021 only | 2022 | R: `ct_refundable_credits`. The amount and child cap are zero outside 2021. The model assumes full take-up and uses 2021 residence as a proxy for domicile at application in 2022. |
| Rhode Island child rebate: `ri_child_tax_rebate`; helper `ri_child_tax_rebate_eligible` | 2021 only | 2022 | R: `ri_refundable_credits`. The amount is zero outside 2021; a true eligibility flag in another year does not imply a payment. |
| Hawaii Act 115 refund: `hi_act_115_rebate` | 2021 only | 2022 | R: `hi_refundable_credits`, removed from the dated list in 2022. Both filing-status schedules are zero before 2021. |
| Maine relief payment: `me_relief_rebate`; helper `me_relief_rebate_eligible` | 2021 only | 2022 | R: `me_refundable_credits`. The $850 amount is zero outside 2021; the eligibility flag alone does not imply a payment. |
| Massachusetts Chapter 62F refund: `ma_taxpayer_refund_rebate` | 2021 only | 2022 | R: `ma_refundable_credits`. Only the 2021 dated list includes it, although its standalone rate persists. |
| Montana HB 192 income tax rebate: `mt_income_tax_rebate` (person level); supporting `mt_income_tax_before_2021_rebate` | 2021 only | 2023 | R: `mt_refundable_credits` adds person-level amounts directly, outside the parameter list. The rebate is liability-capped once per return and zero outside 2021. The separate-versus-joint filing election is determined before the rebate by assumption. |
| South Carolina rebate: `sc_2022_rebate` | 2021 only | 2022 | N: `sc_non_refundable_credits`. The rebate is capped at $800 and eligible liability; the amount is zero outside 2021. |
| Massachusetts essential employee premium pay: `ma_covid_19_essential_employee_premium_pay_program` (person level); input `claimed_ma_covid_19_essential_employee_premium_pay_program_2020` | 2020 and 2021 only | Both modeled rounds paid in 2022 | R: `ma_refundable_credits`. The two $500 rounds use 2020 and 2021 earnings, respectively. The amount is zero before 2020 and from 2022. Set the prior-recipient input in 2021 to exclude a first-round recipient from the second round. The later $250 third round is outside this inventory's coverage. |

The model's first modeled year is 2015. Colorado's 2015 amounts follow the
2015 DR 0104 table (Form 104, line 46); the refund is zero in 2016–2020, when it
was not in effect. Colorado's 2027–2029 tiers are the LCS September 2026
forecast's projections, not published DR 0104 tables, and they stand in until
the State Controller certifies each fiscal year's surplus and CDOR publishes
that year's tiers in the DR 0104.

## Standalone amounts and comparison measures

Illinois's two rebates, New Mexico's three rebates, and Hawaii's Act 115 refund
can return positive standalone amounts after 2021 because their schedules
persist. Their historical guards make the amounts zero before 2021, and the
dated credit totals exclude them after 2021. Arizona and Massachusetts Chapter
62F also have standalone formulas that can remain positive in other years,
while their dated credit lists include them only in 2021.

Maine, Montana, South Carolina, Colorado Cash Back, Connecticut, Rhode Island,
Georgia, New York, and Massachusetts premium pay have amount or formula end
dates. Eligibility helpers and positive standalone amounts are not substitutes
for checking the dated aggregation path and applied liability cap.

The [TAXSIM validation comparison](taxsim.md#how-agreement-is-measured) includes
a rebate-adjusted metric. Its limitations and each program's aggregation path
matter when reconciling that metric with the reported state income tax.

## Pre-rebate comparison output

Two tax-unit outputs restore one-time rebates to state income tax for
comparison with models that report them separately:

```text
state_income_tax_before_one_time_rebates
    = state_income_tax + state_income_tax_rebate_adjustment
```

`state_income_tax_rebate_adjustment` sums the state variables in the
[rebate registry](https://github.com/PolicyEngine/policyengine-us/blob/main/policyengine_us/parameters/gov/states/household/state_income_tax_rebate_adjustments.yaml).
Each restores only the registered rebate amounts that actually reduced that
year's modeled state tax. The comparison liability keeps ordinary credits,
including refundable credits such as state EITCs, so it can be negative.
Neither output changes `state_income_tax`, existing credit totals, or
household net income.

### Scope rule

The registry lists a payment when both of these hold:

1. **The model treats it as one-time.** The state's dated credit list or the
   payment's amount gate limits it to named eligibility years. Standing
   statutes set up some of these payments, such as Massachusetts Chapter 62F
   and Indiana's $125 automatic taxpayer refund, and each paid out in one
   modeled year. Temporary credits that aren't rebate or refund payments, such
   as Arkansas's 2022–2023 inflationary relief credit, stay in liability.
2. **The model credits it against that year's state income tax,** through
   the state's dated credit list or, for Montana, directly in
   `mt_refundable_credits`.

Payments with no end year in the model stay in the comparison liability, even
when they return surplus revenue. That covers Colorado's residual TABOR sales
tax refund (`co_sales_tax_refund`) and Oregon's kicker (`or_kicker`), so the
output restores neither. Only the 2021 list includes Colorado Cash Back
(`co_tabor_cash_back`), so the output restores it. Ordinary recurring credits
also stay in liability.

Under this rule the registry covers every payment in the inventory above
except Colorado's sales tax refund, plus these payments modeled through
refundable credits that the inventory does not list:

| Payment and raw variable(s) | Eligibility year in the dated credit list | Aggregation |
|---|---|---|
| Maine affordability payment: `me_affordability_payment` | 2025 only | R: `me_refundable_credits`, per eligible head or spouse. Legally a direct payment; the model assumes full-year residence and doesn't model the filing deadline. |
| Delaware relief rebate: `de_relief_rebate` | 2020 only | R: `de_refundable_credits`, per modeled head or spouse. |
| Idaho rebates: `id_2022_rebate`, `id_special_season_rebate` | 2020 only in the current model | R: the 2020 list includes both and the 2021 list removes them. Their standalone formulas persist. |
| Indiana automatic refund: `in_automatic_refund_rebate` | 2020 only | R: `in_refundable_credits`. The model leaves out the separate $200 credit on the 2022 return for certain Social Security recipients. |
| New York supplemental EITC payment: `ny_supplemental_eitc` | 2021 only, through its amount gate | R: `ny_refundable_credits`. The dated list includes it from 2019, and its match is zero outside 2021. |
| New York additional Empire State child credit payment: `ny_additional_ctc` | 2021 and 2023 | R: `ny_refundable_credits`. |

A raw rebate amount enters the adjustment only in years when the state's
dated credit list includes it, so a positive standalone amount in another
year contributes zero.

### How the adjustment is computed

This is an additive reconciliation with filing choices and other credit
bases held fixed. It does not rerun taxes with the rebates removed.

- **Refundable rebates** restore the registered amounts in the year's
  refundable-credit list.
- **Massachusetts** Chapter 62F uses liability after other refundable
  credits, including premium pay, as its base. The adjustment restores the
  included amounts and keeps that calculated 62F base.
- **Montana's** separate-versus-joint filing election is determined before
  its 2021 rebate, by model assumption, and the comparison keeps it.
- **Virginia's** rebate is nonrefundable. With before-credit tax `T`, other
  applied nonrefundable credits `C`, rebate `R` and spouse adjustment `S`,
  the adjustment is `max(T - C - S, 0) - max(T - C - R - S, 0)`. A calculated
  `va_rebate` is already limited to tax after the spouse adjustment and
  refundable credits, including the refundable EITC, so the adjustment equals
  it. The formula differs only when a caller supplies a larger `va_rebate`.
- **South Carolina's** rebate is already limited to liability remaining
  after other credits.

If a caller overrides an aggregate credit total or final tax directly, it must
also supply a consistent adjustment; the model cannot infer the rebate share
of an arbitrary total.

### Differences from the TAXSIM dashboard

The dashboard's "Within 1%, net of rebates" column adds a PolicyEngine rebate
amount computed by policyengine-taxsim from its own rebate list. That list is
not this registry, so the column is not a test of
`state_income_tax_before_one_time_rebates`. At the time of writing they differ
for:

- **Oregon:** policyengine-taxsim includes `or_kicker`, because PolicyEngine
  credits the kicker on the return year while TAXSIM reports it for the base
  year. This output leaves the kicker in liability under the scope rule.
- **Massachusetts premium pay** and the **Maine affordability payment:** this
  registry includes them; policyengine-taxsim's list does not.

Both measures restore Colorado Cash Back and leave out Colorado's sales tax
refund. Both also keep New York's inflation refund, supplemental EITC payment
and additional Empire State child credit payment out of the comparison
liability.
