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

## Amounts by year

PolicyEngine sets `gov.states.ak.dor.permanent_fund_dividend` and
`gov.states.ak.dor.energy_relief` to what Alaska paid each eligible person in
each year from 2015, the first year it models:

| Year | Dividend | Energy relief | Source |
|---|---|---|---|
| 2015 | \$2,072 | \$0 | [PFD Division summary table](https://pfd.alaska.gov/division-info/summary-of-dividend-applications-payments); [2019 annual report](https://pfd.alaska.gov/docs/permanentfunddividendlibraries/annual-reports/2019-pfd-annual-report.pdf#page=24) |
| 2016 | \$1,022 | \$0 | Summary table; 2019 annual report |
| 2017 | \$1,100 | \$0 | Summary table; 2019 and [2021](https://pfd.alaska.gov/docs/permanentfunddividendlibraries/annual-reports/2021-pfd-annual-report---final.pdf#page=24) annual reports |
| 2018 | \$1,600 | \$0 | Summary table; 2019 and 2021 annual reports |
| 2019 | \$1,606 | \$0 | Summary table; 2019 and 2021 annual reports |
| 2020 | \$992 | \$0 | Summary table; 2021 annual report |
| 2021 | \$1,114 | \$0 | Summary table; 2021 annual report |
| 2022 | \$2,622 | \$662 | [Alaska DOR release 23-002](https://dor.alaska.gov/docs/default-source/press-releases/2023_02_17-dor-response-to-irs-guidance-on-2022-pfd.pdf#page=1) (Alaska paid \$2,621.81 and \$662.19) |
| 2023 | \$1,312 | \$0 | [2023 annual report](https://pfd.alaska.gov/docs/permanentfunddividendlibraries/annual-reports/2023-pfd-annual-report.pdf#page=3) |
| 2024 | \$1,403.83 | \$298.17 | [Alaska DOR release 24-005](https://dor.alaska.gov/department-of-revenue/news-detail/2024/09/19/department-of-revenue-announces-2024-permanent-fund-dividend-amount-and-energy-relief) |
| 2025 | \$1,000 | \$0 | [Sec. 25(d), ch. 10, SLA 2025](https://www.akleg.gov/PDF/34/Bills/HB0053Z.PDF#page=89); [Alaska DOR release 25-004](https://dor.alaska.gov/department-of-revenue/news-detail/2025/09/22/department-of-revenue-announces-2025-permanent-fund-dividend-amount) |
| 2026 | \$1,000 | \$200 | [Sec. 18(d)](https://www.akleg.gov/PDF/34/Bills/HB0263Z.PDF#page=87) and [sec. 13](https://www.akleg.gov/PDF/34/Bills/HB0263Z.PDF#page=84), ch. 34, SLA 2026; [Alaska DOR release 26-004](https://dor.alaska.gov/department-of-revenue/news-detail/2026/09/28/department-of-revenue-announces-2026-permanent-fund-dividend-amount) |

Alaska sets each year's dividend in its budget and adds energy relief only in
years when it appropriates a one-time payment. It has set no dividend and
appropriated no energy relief for 2027 or later. From 2027, PolicyEngine carries
the 2026 dividend of \$1,000 forward and sets energy relief to zero. To model
amounts that Alaska sets later, supply either variable as an input.

## The 2022 regular dividend and energy relief split

Alaska paid \$3,284 in total: \$2,621.81 of regular PFD and \$662.19 of supplemental
energy relief. PolicyEngine rounds these 2022 components to \$2,622 and \$662,
respectively. Putting the full \$3,284 in `ak_permanent_fund_dividend` would mix
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
