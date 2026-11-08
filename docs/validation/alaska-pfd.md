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
PFD is \$2,622, energy relief is \$662, and federal AGI is \$52,622. With both inputs
set to zero as above, federal AGI is \$50,000.

## The 2022 regular dividend and energy relief split

Alaska paid \$3,284 in total: \$2,621.81 of regular PFD and \$662.19 of supplemental
energy relief. PolicyEngine rounds these 2022 components to \$2,622 and \$662,
respectively. Putting the full \$3,284 in `ak_permanent_fund_dividend` would mix
the components and increase the modeled taxable amount. The split is described
in [Alaska DOR's February 17, 2023
release](https://dor.alaska.gov/docs/default-source/press-releases/2023_02_17-dor-response-to-irs-guidance-on-2022-pfd.pdf#page=1).

## Energy relief in federal gross income

`taxable_ak_energy_relief` holds the part of `ak_energy_relief` in federal gross
income, and `gov.irs.gross_income.ak_energy_relief_excluded` sets that part by
year.

The model leaves the 2022 program's payment out. This follows [IRS IR-2023-23,
including its Alaska
footnote](https://www.irs.gov/newsroom/irs-issues-guidance-on-state-tax-payments-to-help-taxpayers):
the IRS said it would not challenge exclusion of the supplemental energy
payment, while the regular PFD remained taxable. This was a 2022 administrative
nonchallenge policy, rather than a statutory determination for every recipient.
An exclusion under IRC 139 depends on a qualifying disaster and the connection
between the payment and that disaster; see [Notice 2023-56, section
3.04](https://www.irs.gov/pub/irs-drop/n-23-56.pdf#page=6). This model convention
does not establish those facts.

The model also leaves out a payment from the 2022 program that a recipient got
in 2023. In
[section 4.03 of Notice 2023-56](https://www.irs.gov/pub/irs-drop/n-23-56.pdf#page=13),
the IRS addresses the 2022 programs that the news release covered. It lets a
taxpayer who got nothing under such a program in 2022 exclude a payment that
they got under it in 2023. It repeats the rule in
[Publication 525 for 2023](https://www.irs.gov/pub/irs-prior/p525--2023.pdf#page=37).

Alaska paid the 2022 program's energy relief as part of
[one \$3,284 disbursement per eligible Alaskan](https://dor.alaska.gov/docs/default-source/press-releases/2023_02_17-dor-response-to-irs-guidance-on-2022-pfd.pdf#page=1),
so a recipient who got it in 2023 got nothing under the program in 2022. Alaska
paid the \$1,312 dividend for 2023 from the dividend fund's balance and the
Permanent Fund's earnings, with no energy relief
([PFD Division annual report for 2023](https://dor.alaska.gov/docs/permanentfunddividendlibraries/annual-reports/2023-pfd-annual-report.pdf?sfvrsn=6f6d9c6c_1#page=4),
page 4). It paid the relief that the Legislature
[added in 2023](https://dor.alaska.gov/department-of-revenue/news-detail/2024/09/19/department-of-revenue-announces-2024-permanent-fund-dividend-amount-and-energy-relief)
with the 2024 dividend, using \$190.3 million from the general fund
([annual report for 2024](https://dor.alaska.gov/docs/permanentfunddividendlibraries/annual-reports/2024-pfd-annual-report.pdf?sfvrsn=214f2751_1#page=4),
page 4). So every energy relief payment that a recipient got in 2023 came from
the 2022 program, and the model leaves all of them out.

The model counts every payment from 2024 on. In
[section 2 of Notice 2023-56](https://www.irs.gov/pub/irs-drop/n-23-56.pdf#page=2),
the IRS says the news release applied only to payments that states made in
2022. In section 4.03, it adds only 2023 payments under 2022 programs. In
[Publication 525 for 2024](https://www.irs.gov/pub/irs-prior/p525--2024.pdf#page=32),
the IRS tells filers not to reduce Schedule 1 line 8g by the energy relief
portion and treats the entire \$1,702 as taxable. The model's \$1,403.83 of PFD
and \$298.17 of energy relief add up to that. The
[PFD Division](https://pfd.alaska.gov/payments/tax-information) says the \$1,200
dividend for 2026 includes the energy relief payment, and that dividends for
adults "are taxable for federal income tax purposes". The model's \$1,000 and
\$200 add up to that, so an Alaskan adult with \$50,000 of wages has federal AGI
of \$51,200 in 2026.

A payment counts wherever the recipient lives, though the model calculates
`ak_energy_relief` only for Alaska residents. When a dataset or user supplies
energy relief or a regular dividend for someone who has since moved, the amount
stays in federal gross income.
