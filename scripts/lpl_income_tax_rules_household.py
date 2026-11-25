"""Household example for the retirement, capital gain and lot-level rules.

Run:  python scripts/lpl_income_tax_rules_household.py [STATE]

A single filer, age 45, has $90,000 of wages, a $20,000 early IRA
distribution with no exception, a $10,000 net gain on regulated futures
(section 1256 contracts) and two lots:
- a $1,000 qualified dividend on stock held 50 days around the ex-date, and
- a $1,000 short-term loss sale repurchased 10 days later (a wash sale).

"Before" is how a caller without the new fields reports this: the futures
gain as short-term, the dividend as qualified, the loss deducted, and no
early-distribution tax. "After" sends the new fields; the lot results are
folded in with apply_investment_lot_adjustments.
"""

import sys

from policyengine_us import Simulation
from policyengine_us.tools.investment_lots import apply_investment_lot_adjustments

YEAR = 2026
STATE = sys.argv[1] if len(sys.argv) > 1 else "TX"


def situation(after: bool) -> dict:
    person = {
        "age": 45,
        "employment_income": 90_000,
        "taxable_ira_distributions": 20_000,
        "qualified_dividend_income": 1_000,
    }
    if after:
        person.update(
            {
                "early_distributions_from_retirement_plans": 20_000,
                "section_1256_net_gain": 10_000,
                "dividend_lot_1_qualified_dividends_reported": 1_000,
                "dividend_lot_1_days_held_in_window": 50,
                "wash_sale_1_loss": 1_000,
                "wash_sale_1_shares_sold": 100,
                "wash_sale_1_sale_day": 9_400,
                "wash_sale_1_purchase_1_day": 9_410,
                "wash_sale_1_purchase_1_shares": 100,
            }
        )
    else:
        person.update({"short_term_capital_gains": 10_000 - 1_000})
    return {
        "people": {"filer": {k: {str(YEAR): v} for k, v in person.items()}},
        "tax_units": {
            "tax_unit": {"members": ["filer"], "filing_status": {str(YEAR): "SINGLE"}}
        },
        "households": {
            "household": {"members": ["filer"], "state_code": {str(YEAR): STATE}}
        },
    }


def results(after: bool) -> dict:
    sit = situation(after)
    if after:
        sit = apply_investment_lot_adjustments(sit, YEAR)
    sim = Simulation(situation=sit)

    def calc(variable):
        return float(sim.calculate(variable, YEAR).sum())

    out = {
        "Federal AGI": calc("adjusted_gross_income"),
        "Long-term capital gains": calc("long_term_capital_gains"),
        "Short-term capital gains": calc("short_term_capital_gains"),
        "Qualified dividends": calc("qualified_dividend_income"),
        "Taxable income": calc("taxable_income"),
        "Early distribution tax": calc("form_5329_additional_taxes"),
        "Federal income tax": calc("income_tax"),
    }
    if STATE == "CA":
        out["CA early distribution tax"] = calc("ca_early_distribution_additional_tax")
    out["State income tax"] = calc("state_income_tax")
    return out


if __name__ == "__main__":
    before, after = results(False), results(True)
    print(f"{STATE} {YEAR}, single filer")
    print(f"{'':28}{'before':>14}{'after':>14}{'change':>12}")
    for label in after:
        b, a = before.get(label, 0.0), after[label]
        print(f"{label:28}{b:>14,.2f}{a:>14,.2f}{a - b:>12,.2f}")
