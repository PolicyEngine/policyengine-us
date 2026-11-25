"""Household example: a state subtraction for mutual fund dividends attributable
to U.S. government obligations, through the normal Simulation API.

Run:  python scripts/us_govt_fund_dividends_household.py [STATE]

A single filer in the state (default NY) has $100,000 of wages and $3,000 of
ordinary dividends from two funds in a taxable account:

- Fund 1, a Treasury fund: $1,000 of dividends, 35% from U.S. government
  obligations, at exactly 50% of assets in U.S. government obligations at
  every fiscal quarter-end. It passes the 50% test.
- Fund 2, a government money market fund: $2,000 of dividends, 80% from U.S.
  government obligations, 49.99% at one quarter-end. It fails, though its
  annual income share is above 50%.

"Before" omits the fund fields, which is how an existing caller looks; "after"
adds them. Only fund 1 contributes: $1,000 x 35% = $350.
"""

import sys

from policyengine_us import Simulation

YEAR = "2026"
STATE = sys.argv[1] if len(sys.argv) > 1 else "NY"

# The fields the portfolio simulator sends for each fund slot, per person.
FUND_FIELDS = {
    # Fund 1: passes at exactly 50% every quarter-end.
    "us_govt_fund_1_ordinary_dividends": 1_000,
    "us_govt_fund_1_govt_income_share": 0.35,
    "us_govt_fund_1_govt_asset_share_q1": 0.50,
    "us_govt_fund_1_govt_asset_share_q2": 0.50,
    "us_govt_fund_1_govt_asset_share_q3": 0.50,
    "us_govt_fund_1_govt_asset_share_q4": 0.50,
    "us_govt_fund_1_asset_test_evidence": "QUARTERLY_ASSET_SHARES",
    "us_govt_fund_1_qualified_fund_of_funds": False,
    # Fund 2: fails in quarter 2.
    "us_govt_fund_2_ordinary_dividends": 2_000,
    "us_govt_fund_2_govt_income_share": 0.80,
    "us_govt_fund_2_govt_asset_share_q1": 0.70,
    "us_govt_fund_2_govt_asset_share_q2": 0.4999,
    "us_govt_fund_2_govt_asset_share_q3": 0.70,
    "us_govt_fund_2_govt_asset_share_q4": 0.70,
    "us_govt_fund_2_asset_test_evidence": "QUARTERLY_ASSET_SHARES",
    "us_govt_fund_2_qualified_fund_of_funds": False,
}


def situation(with_funds: bool) -> dict:
    person = {
        "age": 45,
        "employment_income": 100_000,
        # The simulator already reports every fund dividend here.
        "non_qualified_dividend_income": 3_000,
    }
    if with_funds:
        person.update(FUND_FIELDS)
    return {
        "people": {"filer": {k: {YEAR: v} for k, v in person.items()}},
        "tax_units": {
            "tax_unit": {"members": ["filer"], "filing_status": {YEAR: "SINGLE"}}
        },
        "households": {
            "household": {"members": ["filer"], "state_code": {YEAR: STATE}}
        },
    }


def results(with_funds: bool) -> dict:
    sim = Simulation(situation=situation(with_funds))
    s = STATE.lower()

    def calc(variable):
        return float(sim.calculate(variable, int(YEAR)).sum())

    return {
        "Federal AGI": calc("adjusted_gross_income"),
        "State fund dividend subtraction": calc(
            f"{s}_us_govt_fund_dividend_subtraction"
        ),
        "State AGI": calc(f"{s}_agi"),
        "State taxable income": calc(f"{s}_taxable_income"),
        "State income tax": calc(f"{s}_income_tax"),
    }


if __name__ == "__main__":
    before = results(with_funds=False)
    after = results(with_funds=True)
    print(f"{STATE} {YEAR}, single filer")
    print(f"{'':34}{'before':>14}{'after':>14}{'change':>12}")
    for label in before:
        b, a = before[label], after[label]
        print(f"{label:34}{b:>14,.2f}{a:>14,.2f}{a - b:>12,.2f}")
