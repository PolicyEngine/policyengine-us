# Fund dividends from U.S. government obligations

Federal law bars states from taxing interest on U.S. government obligations
(31 U.S.C. § 3124). A shareholder who receives that interest through a
regulated investment company (a mutual fund, ETF or money market fund) gets
the exemption only as each state's law passes it through. California,
Connecticut and New York pass it through only for a fund that holds at least
50% of the value of its total assets in qualifying obligations **at the close
of each quarter of the fund's taxable year**. PolicyEngine models that test
fund by fund.

## Rules modeled

| State | Subtraction | Asset test | Line |
|---|---|---|---|
| California | `ca_us_govt_fund_dividend_subtraction` | ≥ 50% of total assets in obligations exempt from California tax at each quarter-end; a qualified fund of funds (IRC 852(g)(2)) is exempt from the test from 2011 | Schedule CA (540), line 2, column B |
| Connecticut | `ct_us_govt_fund_dividend_subtraction` | ≥ 50% of total assets (IRC 851(c)(4)) in obligations that federal law bars states from taxing, at each quarter-end | CT-1040, line 40 |
| New York | `ny_us_govt_fund_dividend_subtraction` | ≥ 50% of total assets in U.S. obligations at each quarter-end | IT-201, line 28 |

Sources: Cal. Rev. & Tax. Code § 17145; Conn. Gen. Stat. § 12-718 and Conn.
Agencies Regs. § 12-701(a)(20)-3; N.Y. Tax Law § 612(c)(1) and TSB-M-92(4)I.

Direct holdings of U.S. obligations stay on `us_govt_interest_person` (or
`us_govt_interest`), which every state already subtracts. Do not put fund
dividends there: each subtraction is counted once, from its own input.

## Inputs per fund

Each person has 10 fund slots, `us_govt_fund_1_*` to `us_govt_fund_10_*`.
Use one slot per fund held in a taxable account and never merge funds.

| Field | Type | Meaning |
|---|---|---|
| `us_govt_fund_<n>_ordinary_dividends` | USD | Ordinary dividends from the fund (Form 1099-DIV box 1a; no capital gain distributions). A memo of dividends already in `qualified_dividend_income` / `non_qualified_dividend_income`; it adds no income. |
| `us_govt_fund_<n>_govt_income_share` | 0–1 | Share of the fund's ordinary dividends from U.S. government obligations, from the issuer's annual tax supplement. Sets the amount only. |
| `us_govt_fund_<n>_govt_asset_share_q1` … `_q4` | 0–1 | Share of total assets in qualifying U.S. government obligations at the close of each quarter of the fund's taxable year. Sets eligibility only. |
| `us_govt_fund_<n>_asset_test_evidence` | enum | `QUARTERLY_ASSET_SHARES` (default), `ISSUER_CONFIRMED_MET` or `ISSUER_CONFIRMED_NOT_MET`. |
| `us_govt_fund_<n>_qualified_fund_of_funds` | bool | Qualified fund of funds; used only by California. |

Subtraction per fund = `ordinary_dividends × govt_income_share` if the fund
passes the state's test, else 0. The person's total is capped at
`ordinary_dividend_income`, and dependents' amounts stay off the filer's
return.

### Using an issuer's annual tax supplement

Issuers publish a "percentage of income from U.S. government obligations"
table each January or February. Use it this way:

1. `govt_income_share` = the fund's percentage for the calendar year, as a
   fraction (98.67% → `0.9867`).
2. If the supplement states that the fund met the California, Connecticut
   and New York 50% requirement, set `asset_test_evidence` to
   `ISSUER_CONFIRMED_MET`. If it marks the fund as not meeting it (often an
   asterisk), set `ISSUER_CONFIRMED_NOT_MET`.
3. If the supplement says nothing about the test, supply the four quarter-end
   asset shares from the fund's holdings reports (N-PORT, N-MFP or annual and
   semi-annual reports) and leave the evidence at `QUARTERLY_ASSET_SHARES`.

The income percentage never establishes the asset test. A fund can report
more than 50% of income from U.S. obligations and still fail a quarter.

### What counts toward the asset share

Count U.S. Treasury bills, notes, bonds and savings bonds, and obligations of
agencies whose interest federal law exempts from state tax (for example
Federal Farm Credit Banks, Federal Home Loan Banks and the Tennessee Valley
Authority). Do not count repurchase agreements, even when Treasuries
collateralize them (NY TSB-M-88(5)I; Appeal of H. Lon Henry, Cal. SBE), or
Ginnie Mae, Fannie Mae and Freddie Mac securities (Conn. Agencies Regs.
§ 12-701(a)(20)-3). Measure at the close of each quarter of the **fund's**
taxable year, which need not be the calendar year.

California's asset base also counts California municipal obligations, and
Connecticut's counts territorial obligations. The slots carry U.S. government
obligations only, so for a fund that reaches 50% only with those holdings,
use the issuer's statement.

### Missing data

Every quarterly share defaults to 0, which fails the test. A fund with fewer
than four quarter-end shares, or with only an income share, gets no
subtraction. Supply the issuer's statement instead for a fund whose first
taxable year was shorter than four quarters.

## Example

`scripts/us_govt_fund_dividends_household.py` runs a New York household
through `Simulation` with two funds, one passing and one failing.

## Not modeled

States without a 50% asset test (most others) let shareholders subtract the
U.S. government share of fund dividends. They are not wired to these slots
yet. New Jersey's separate 80% "qualified investment fund" rule
(N.J.S.A. 54A:6-14.1) is also not modeled.
