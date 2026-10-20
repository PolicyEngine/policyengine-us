# Alaska Permanent Fund Dividend in model comparisons

PolicyEngine automatically calculates `ak_permanent_fund_dividend` and
`ak_energy_relief` for each person whose household is in Alaska. These amounts
are calculated benefits, rather than imputed income or fixed default inputs.
Current Alaska residence is an eligibility proxy: the model does not check an
application, prior-year residence, or actual receipt. Supplying wages and other
known income does not disable either calculation.

The regular PFD is included in federal gross income for nondependent people.
A dependent child's PFD is not automatically added to the parent's adjusted
gross income (AGI). Tax-unit membership alone does not determine dependent
status; supply explicit roles or dependent status when constructing a household.
The regular dividend appears on [2022 Schedule 1, line
8g](https://www.irs.gov/pub/irs-prior/f1040s1--2022.pdf#page=1).

## Override calculated payments

Supply either variable as an input on the person to replace its calculated
amount. To exclude both transfers from a controlled comparison, set both to zero
for **every person**. Overriding only `ak_permanent_fund_dividend` leaves energy
relief in place. Overriding only tax-unit AGI leaves the underlying person income
and benefit amounts unchanged.

This complete situation retains Alaska residence while excluding both payments:

```yaml
people:
  person:
    age: {2022: 40}
    employment_income: {2022: 50000}
    ak_permanent_fund_dividend: {2022: 0}
    ak_energy_relief: {2022: 0}
tax_units:
  tax_unit:
    members: [person]
households:
  household:
    members: [person]
    state_code: {2022: AK}
```

With only the two payment inputs removed, this person's calculated 2022 regular
PFD is $2,622, energy relief is $662, and federal AGI is $52,622. With both inputs
set to zero as above, federal AGI is $50,000.

## The 2022 regular dividend and energy relief split

Alaska paid $3,284 in total: $2,621.81 of regular PFD and $662.19 of supplemental
energy relief. PolicyEngine rounds these 2022 components to $2,622 and $662,
respectively. Putting the full $3,284 in `ak_permanent_fund_dividend` would mix
the components and increase the modeled taxable amount. The split is described
in [Alaska DOR's February 17, 2023
release](https://dor.alaska.gov/docs/default-source/press-releases/2023_02_17-dor-response-to-irs-guidance-on-2022-pfd.pdf#page=1).

The model excludes the separate energy payment from federal gross income. For
2022, this follows [IRS IR-2023-23, including its Alaska
footnote](https://www.irs.gov/newsroom/irs-issues-guidance-on-state-tax-payments-to-help-taxpayers):
the IRS said it would not challenge exclusion of the supplemental energy
payment, while the regular PFD remained taxable. This was a 2022 administrative
nonchallenge policy, rather than a statutory determination for every recipient.
An exclusion under IRC 139 depends on a qualifying disaster and the connection
between the payment and that disaster; see [Notice 2023-56, section
3.04](https://www.irs.gov/pub/irs-drop/n-23-56.pdf#page=6). This model convention
does not establish those facts or extend the 2022 IRS policy to other years.
