# State rebates in model comparisons

PolicyEngine attributes one-time state rebates to the tax year whose return
determines eligibility and amount, even when checks arrive in a later calendar
year. Rebates included in state credit totals reduce `state_income_tax` and
increase household net income in that eligibility year. This attribution
convention does not describe the payment calendar. Some standalone rebate
formulas can calculate an amount after the rebate ends; use the dated credit
total to establish whether that amount enters tax or net income. Do not add
back every positive raw rebate column in every year. Massachusetts premium pay
is also modeled through state refundable credits. A payment modeled solely as a
benefit would affect household net income without reducing state income tax.

For comparison, restore only the rebate amounts that actually reduced that
year's reported state tax, including liability limits on nonrefundable credits.
Ordinary recurring refundable credits remain part of liability.
`state_income_tax_before_refundable_credits` removes those ordinary credits too,
so it is not a pre-rebate liability measure. Colorado Cash Back and the residual
TABOR sales tax refund are separate mechanisms; count each only through its
stated aggregation path and eligibility year.

## Comparison outputs

Two tax-unit outputs provide this reconciliation:

```text
state_income_tax_before_one_time_rebates
    = state_income_tax + state_income_tax_rebate_adjustment
```

`state_income_tax_rebate_adjustment` restores the registered rebate amounts
actually included in the year's modeled state tax. The comparison liability
retains ordinary credits, including refundable credits such as state EITCs.
It can therefore be negative. Neither output changes canonical
`state_income_tax`, existing credit totals, or household net income.

The [rebate registry](https://github.com/PolicyEngine/policyengine-us/blob/main/policyengine_us/parameters/gov/states/household/state_income_tax_rebate_adjustments.yaml)
identifies the state effects within the comparison's scope. A registry entry
does not establish a payment in every year. State effects follow canonical
credit aggregation and calculated amounts, including dated credit lists,
formula dates, and amount gates. Montana's rebate is added directly by
`mt_refundable_credits`, rather than through its credit list. For example,
a positive raw `il_income_tax_rebate` after 2021
is excluded from Illinois's refundable-credit list and contributes zero to the
adjustment. Amounts that are zero contribute zero even if a dated list retains
the variable.

Despite the comparison output's name, its scope includes Colorado's residual
TABOR sales tax refund, which is a recurring statutory mechanism. It also
includes Massachusetts essential employee premium pay and Maine's 2025
affordability payment, because these payments currently reduce modeled state
income tax through refundable-credit aggregation.

This is an additive reconciliation with all existing filing choices and other
credit bases held fixed. It does not rerun taxes under a counterfactual policy
with the rebates removed. In particular:

- Massachusetts Chapter 62F uses liability after other refundable credits,
  including premium pay, as its base. The adjustment restores the included
  amounts while retaining that calculated 62F base.
- Montana's separate-versus-joint filing election is determined before its
  2021 rebate by model assumption. The comparison retains that election.
- Virginia's face rebate can exceed its effect on final tax. The adjustment
  respects other nonrefundable credits, the subsequent spouse adjustment,
  and the final zero floor. With before-credit tax `T`, other applied credits
  `C`, rebate `R`, and spouse adjustment `S`, its effect is
  `max(T - C - S, 0) - max(T - C - R - S, 0)`.
- South Carolina's rebate is already limited to liability remaining after
  other credits. Georgia and Montana rebates are modeled as refundable.

The adjustment follows canonical credit paths. If a caller overrides an aggregate
credit total or final tax directly, it must also supply a consistent rebate
adjustment; the model cannot infer the rebate share of an arbitrary total.

## Included payments and current timing

The following inventory describes contributions to **current modeled tax
totals**, including existing historical backdating. It is not a statement that
every listed year has a legal entitlement. `R` denotes a state's refundable
credit total; `N` denotes its nonrefundable total. All these payments flow
through state credits, rather than a second direct household benefit payment.

| Payment and raw variable(s) | Years with a possible nonzero contribution to current tax totals | Aggregation and timing |
|---|---|---|
| Colorado residual TABOR sales refund: `co_sales_tax_refund` | 2015–2025; 2026 is zero; 2027 onward under carried-forward parameters | R; amount, eligible-filer count, and `in_effect` gate. This is separate from Cash Back. Historical and future limitations are below. |
| Colorado Cash Back: `co_tabor_cash_back` | 2021 only | R; based on the 2021 return and paid in 2022. Both the amount and dated credit list end after 2021. |
| Illinois income and property: `il_income_tax_rebate`, `il_property_tax_rebate` | 2015–2021; intended eligibility year 2021 | R; paid in 2022, based on the 2021 return. The list removes both in 2022; missing earlier guards allow pre-2021 contributions. |
| New York inflation refund: `ny_inflation_refund_credit` | 2023 only | R; paid in 2025, based on the 2023 return. Formula dates reset it to zero after 2023. |
| Virginia: `va_rebate` | 2015–2022 and 2024; intended eligibility years 2021, 2022, and 2024 | N; the intended return years correspond to payments in 2022, 2023, and 2025. Amounts are zero in 2023 and from 2025; missing earlier guards allow pre-2021 contributions. The adjustment uses the final-tax effect. |
| Georgia surplus: `ga_surplus_tax_rebate` | 2021 only | R; modeled under O.C.G.A. 48-7-20.2 from 2021 liability, paid later. It is capped at income tax before credits and has zero amounts outside 2021. |
| Arizona families: `az_families_tax_rebate` | 2021 only | R; paid in 2023, based on the 2021 return. The dated list controls inclusion even when a standalone formula returns a positive value elsewhere. |
| New Mexico: `nm_2021_income_rebate`, `nm_additional_2021_income_rebate`, `nm_supplemental_2021_income_rebate` | 2015–2021; intended eligibility year 2021 | R; enacted in 2022 or 2023 but based on the 2021 return. The list removes all three in 2022; missing earlier guards allow pre-2021 contributions. |
| Connecticut child: `ct_child_tax_rebate` | 2021 only | R; paid in 2022, based on the 2021 return. Amount and child-cap gates are zero outside 2021. Full take-up is assumed; 2021 residence proxies for domicile at application. |
| Rhode Island child: `ri_child_tax_rebate` | 2021 only | R; paid in 2022, based on the 2021 return. The amount is zero outside 2021. |
| Hawaii Act 115: `hi_act_115_rebate` | 2015–2021; intended eligibility year 2021 | R; paid in 2022, based on the 2021 return. The list removes it in 2022; missing earlier guards allow pre-2021 contributions. |
| Maine \$850 relief: `me_relief_rebate` | 2021 only | R; paid in 2022, based on the 2021 return. The amount is zero outside 2021. |
| Massachusetts Chapter 62F: `ma_taxpayer_refund_rebate` | 2021 only | R; paid in 2022, based on 2021 liability. The rate persists in standalone calculations, but the dated list includes it only in 2021. |
| Montana HB 192: `mt_income_tax_rebate` | 2021 only | R; person amounts are added directly by `mt_refundable_credits`. Paid in 2023, based on 2021 liability. The amount is zero outside 2021 and capped once per return. |
| South Carolina: `sc_2022_rebate` | 2021 only | N; paid in 2022, based on the 2021 return. Capped at \$800 and residual liability; the amount is zero outside 2021. |
| Massachusetts premium pay: `ma_covid_19_essential_employee_premium_pay_program` | 2015–2021; intended eligibility years 2020 and 2021 | R; person amounts for two modeled \$500 rounds paid in 2022. Missing earlier guards allow pre-2020 contributions. The variable remains listed later, with a zero amount from 2022. |
| Maine affordability: `me_affordability_payment` | 2025 only | R; \$300 per eligible head or spouse, based on the 2025 return. Both dated inclusion and amount gates end in 2026. The payment is legally a direct payment; this model exposes it through refundable credits. |
| Delaware relief: `de_relief_rebate` | 2020 only | R; \$300 per modeled head or spouse, based on the 2020 eligibility return and paid in 2022. Both dated inclusion and amount gates restrict it to 2020. |
| Idaho: `id_2022_rebate`, `id_special_season_rebate` | 2020 only in the current model | R; the 2020 list includes both; the 2021 list removes them. Their standalone amount/rate formulas persist. This inventory records current model attribution without revising the mapping of these named rebates to return years. |
| Indiana automatic refund: `in_automatic_refund_rebate` | 2020 only | R; modeled \$125 plus \$200 per head or spouse, based on the 2020 eligibility return and paid in 2022. Both dated inclusion and amount gates restrict it to 2020. The separate \$200 credit for certain Social Security recipients on the 2022 return is outside this modeled component. |

The Maine affordability, Delaware, Idaho, and Indiana rows supplement the
original comparison inventory. For Maine, the model assumes full-year residence
and does not model the return-filing deadline; recipient-level dependent
disqualifications still apply. For Massachusetts premium pay, this inventory
describes the two modeled \$500 rounds and does not claim coverage of the later
\$250 round.

## Historical and future coverage limits

Model parameter construction backdates each parameter's first value to 2015,
the first modeled year. Without an earlier zero amount or a credit-list entry
excluding a rebate, this can produce a contribution before its intended
eligibility year. Existing examples include Illinois, New Mexico, Hawaii, and
Virginia before 2021, and Massachusetts premium pay before 2020. Colorado's
sales refund also remains active in the modeled 2016–2020 period despite the
historical availability restriction. The comparison output restores these
amounts when they reduced modeled tax; it does not correct those historical
eligibility errors or change the attribution convention.

The 2015 start in the table reflects model coverage, not a program's enactment
date. Colorado's backdated amount schedule is not a verified 2015 refund table.
Its 2027-and-later inclusion reflects current carried-forward parameters;
post-2026 amounts use placeholders pending published tables. These entries do
not verify future payments.

A positive raw amount or eligibility flag alone is insufficient to establish
an effect on tax. Illinois, Arizona, New Mexico, Hawaii, Massachusetts 62F,
and Idaho have standalone formulas that can remain positive outside their
included years. Use the comparison adjustment or inspect dated credit-list
membership and amount gates together when reconciling external model outputs.
