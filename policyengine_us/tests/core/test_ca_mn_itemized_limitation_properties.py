"""Invariants of the California and Minnesota high-income itemized limitations.

California (R&TC 17077, adopting 26 U.S.C. 68) and Minnesota (Minn. Stat.
290.0122, subd. 2(d)) reduce itemized deductions of high-income filers, but
leave medical expenses, investment interest and casualty and theft losses out
of the deductions the reduction is computed on.

Every tax unit in a grid of states, filing statuses, incomes and deductions
shares one simulation per year. Each unit has twins that differ only in their
investment interest, and one that differs only in having no income. With the
deduction inputs set directly, income changes only the reduction, so the
no-income twin carries the pre-limitation total. For every unit:

1. The deduction lies between 0 and its pre-limitation total.
2. The reduction (pre-limitation total less the deduction) does not change
   with investment interest, since investment interest is never reduced.
"""

from itertools import product

import numpy as np
import pytest

from policyengine_us import Simulation

YEARS = (2024, 2026)
STATES = ("CA", "MN")
FILING_STATUSES = ("SINGLE", "JOINT")
AGIS = (0, 150_000, 300_000, 600_000, 2_000_000)
CHARITY = (0, 10_000)
MEDICAL = (0, 4_000)
# (investment interest paid, investment expenses). With expenses, California's
# FTB 3526 deduction is below the interest paid, so the federal and
# California amounts differ.
INVESTMENT = ((0, 0), (10_000, 0), (10_000, 4_000), (5_000, 20_000))

UNITS = list(product(STATES, FILING_STATUSES, AGIS, CHARITY, MEDICAL, INVESTMENT))


def _simulation(year):
    period = str(year)
    people, tax_units, households = {}, {}, {}
    for i, (state, status, agi, charity, medical, investment) in enumerate(UNITS):
        interest, expenses = investment
        person = f"p{i}"
        people[person] = {
            "age": {period: 50},
            "investment_interest_expense": {period: interest},
            "investment_expenses": {period: expenses},
        }
        tax_units[f"t{i}"] = {
            "members": [person],
            "filing_status": {period: status},
            "adjusted_gross_income": {period: agi},
            "charitable_deduction": {period: charity},
            "ca_charitable_deduction": {period: charity},
            "medical_expense_deduction": {period: medical},
        }
        households[f"h{i}"] = {"members": [person], "state_code": {period: state}}
    return Simulation(
        situation={"people": people, "tax_units": tax_units, "households": households}
    )


def _index(state, status, agi, charity, medical, investment):
    return UNITS.index((state, status, agi, charity, medical, investment))


@pytest.mark.parametrize("year", YEARS)
def test_itemized_limitation_invariants(year):
    period = str(year)
    simulation = _simulation(year)
    deduction = {
        "CA": simulation.calculate("ca_itemized_deductions", period),
        "MN": simulation.calculate("mn_itemized_deductions", period),
    }
    ca_pre = simulation.calculate("ca_itemized_deductions_pre_limitation", period)

    for i, (state, status, agi, charity, medical, investment) in enumerate(UNITS):
        label = f"{year} {UNITS[i]}"
        pre = deduction[state][_index(state, status, 0, charity, medical, investment)]
        if state == "CA":
            assert ca_pre[i] == pytest.approx(pre, abs=0.01), label
        value = deduction[state][i]

        # 1. The deduction lies between 0 and the pre-limitation total.
        assert value >= 0, label
        assert value <= pre + 0.01, label

        # 2. Investment interest does not change the reduction.
        j = _index(state, status, agi, charity, medical, (0, 0))
        k = _index(state, status, 0, charity, medical, (0, 0))
        reduction_without = deduction[state][k] - deduction[state][j]
        assert pre - value == pytest.approx(reduction_without, abs=0.01), label
