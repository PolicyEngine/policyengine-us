"""Fold lot-level results into PolicyEngine's aggregate income inputs.

short_term_capital_gains, the dividend inputs and taxable_interest_income
are plain inputs (their datasets are uprated), so computed short-term,
dividend and interest results cannot flow into them by formula. This helper
runs one pass to compute those results from the lot-level inputs and returns
a situation with them applied, ready for the normal Simulation. Long-term
results already flow into long_term_capital_gains by formula and are left
alone.

Usage:
    from policyengine_us import Simulation
    from policyengine_us.tools.investment_lots import apply_investment_lot_adjustments
    sim = Simulation(situation=apply_investment_lot_adjustments(situation, 2026))
"""

import copy

# Computed variable -> [(input it adjusts, sign)].
ADJUSTMENTS = {
    "short_term_capital_gain_adjustments": [("short_term_capital_gains", 1)],
    "investment_lot_interest_adjustment": [("taxable_interest_income", 1)],
    "dividends_failing_qualified_holding_period": [
        ("qualified_dividend_income", -1),
        ("non_qualified_dividend_income", 1),
    ],
    "section_199a_dividends_failing_holding_period": [
        ("qualified_reit_and_ptp_income", -1),
    ],
}


def apply_investment_lot_adjustments(situation: dict, year) -> dict:
    from policyengine_us import Simulation

    year = str(year)
    sim = Simulation(situation=situation)
    people = list(situation["people"])
    adjusted = copy.deepcopy(situation)
    for computed, targets in ADJUSTMENTS.items():
        values = sim.calculate(computed, int(year))
        for person_id, value in zip(people, values):
            if value == 0:
                continue
            person = adjusted["people"][person_id]
            for target, sign in targets:
                current = person.get(target, {}).get(year, 0)
                person.setdefault(target, {})[year] = float(current) + sign * float(
                    value
                )
    return adjusted
