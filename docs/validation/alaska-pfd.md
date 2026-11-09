# Alaska Permanent Fund Dividend in model comparisons

PolicyEngine automatically calculates `ak_permanent_fund_dividend` and
`ak_energy_relief` for each person who lives in Alaska, holds an immigration
status the dividend statute names, and takes up the dividend. These amounts are
calculated benefits, rather than imputed income or fixed default inputs. The
model has no inputs for the statute's other tests: an application, residence
during all of the prior calendar year, allowable absences, or a felony sentence
or conviction-based incarceration during that year. `is_incarcerated` does not
say why a person is incarcerated or tie to that year, so it does not affect the
dividend. Supplying wages and other known income does not disable either
calculation.

The regular PFD is included in federal gross income for nondependent people.
A dependent child's PFD is not automatically added to the parent's adjusted
gross income (AGI). Tax-unit membership alone does not determine dependent
status; supply explicit roles or dependent status when constructing a household.
The regular dividend appears on [2022 Schedule 1, line
8g](https://www.irs.gov/pub/irs-prior/f1040s1--2022.pdf#page=1).

## Who receives the dividend

`ak_permanent_fund_dividend_eligible` applies the status test in [AS
43.23.005(a)(5)](https://www.akleg.gov/basis/statutes.asp#43.23.005): a citizen, a
lawful permanent resident, a refugee, or an asylee. [15 AAC
23.154(a)](https://www.akleg.gov/basis/aac.asp#15.23.154) also counts conditional
permanent residents and people on indefinite parole as lawfully admitted for
permanent residence. PolicyEngine has no status for either, so code them as
`LEGAL_PERMANENT_RESIDENT`. `PAROLED_ONE_YEAR`, `CUBAN_HAITIAN_ENTRANT` and
`CONDITIONAL_ENTRANT` do not say whether a parole runs indefinitely or whether
the person may adopt the United States as their domicile, so they stay out.

`takes_up_ak_permanent_fund_dividend_if_eligible` covers the statute's other
tests and anyone who does not apply. It defaults to true, so a household
calculation pays every eligible Alaska resident unless an input says otherwise.
Set it to false for a person Alaska did not pay. Both variables gate
`ak_energy_relief` as well, because Alaska pays energy relief as part of the
dividend ([sec. 13, ch. 34, SLA
2026](https://www.akleg.gov/PDF/34/Bills/HB0263Z.PDF#page=84)).

### Recipients in microsimulation

Populace does not set `takes_up_ak_permanent_fund_dividend_if_eligible` yet, so
the default microsimulation pays everyone who passes the status test: 730,150
people for 2024, against the [624,489 applications Alaska
paid](https://pfd.alaska.gov/division-info/summary-of-dividend-applications-payments)
for that dividend year. The Microcosm data pipeline can close that gap by setting
the flag from reported receipt and Alaska's paid count; see
[microcosm issue 1551](https://github.com/PolicyEngine/microcosm/issues/1551).
The microsimulation has no inputs before its 2024 base year, so it cannot report
recipients for earlier years.

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
