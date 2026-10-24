"""Oregon's federal tax liability subtraction follows the OR-17 worksheet.

ORS 316.680(1)(b) and 316.685; Publication OR-17, federal tax worksheet,
Part A. The subtraction is federal tax after nonrefundable credits plus other
income taxes, less only the refundable credits the worksheet lists, floored at
zero and capped by federal AGI. These properties hold for every input:

1. 0 <= subtraction <= min(federal tax before refundable credits, cap).
2. The earned income credit never changes it (ORS 316.685(1)(b)), and outside
   2021 neither does the additional child tax credit.
3. Raising a listed credit (the premium tax credit) by d lowers it by at most d.
4. Raising federal tax before refundable credits by d raises it by at most d.

Each Hypothesis example evaluates a batch of tax units and their variants in
one vectorized simulation.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01
FILING_STATUSES = ("SINGLE", "JOINT", "HEAD_OF_HOUSEHOLD", "SEPARATE")
CREDITS = (
    "eitc",
    "refundable_ctc",
    "refundable_american_opportunity_credit",
    "assigned_aca_ptc",
    "recovery_rebate_credit",
    "cdcc",
)
VARIANTS = ("base", "eitc", "refundable_ctc", "assigned_aca_ptc", "tax")


@st.composite
def tax_unit(draw):
    return {
        "filing_status": draw(st.sampled_from(FILING_STATUSES)),
        "adjusted_gross_income": draw(st.integers(0, 300_000)),
        "income_tax_before_refundable_credits": draw(st.integers(0, 20_000)),
        "net_investment_income_tax": draw(st.integers(0, 2_000)),
        "unreported_payroll_tax": draw(st.integers(0, 1_000)),
        **{credit: draw(st.integers(0, 6_000)) for credit in CREDITS},
        "delta": draw(st.integers(1, 5_000)),
    }


def _run(units, year):
    situation = {"people": {}, "tax_units": {}, "households": {}}
    rows = []
    for i, unit in enumerate(units):
        for variant in VARIANTS:
            inputs = {k: v for k, v in unit.items() if k != "delta"}
            if variant == "tax":
                inputs["income_tax_before_refundable_credits"] += unit["delta"]
            elif variant != "base":
                inputs[variant] += unit["delta"]
            name = f"{i}_{variant}"
            situation["people"][name] = {"age": {year: 40}}
            situation["tax_units"][name] = {
                "members": [name],
                **{k: {year: v} for k, v in inputs.items()},
            }
            situation["households"][name] = {
                "members": [name],
                "state_code": {year: "OR"},
            }
            rows.append((i, variant))
    simulation = Simulation(situation=situation)
    values = simulation.calculate("or_federal_tax_liability_subtraction", year)
    result = {}
    for (i, variant), value in zip(rows, values):
        result.setdefault(i, {})[variant] = float(value)
    # The largest cap, at zero AGI, from the simulation's own parameters.
    p = (
        simulation.tax_benefit_system.parameters(f"{year}-01-01")
        .gov.states["or"]
        .tax.income.subtractions.federal_tax_liability.cap
    )
    zero = np.array([0.0])
    cap = {
        "SINGLE": p.single.calc(zero)[0],
        "JOINT": p.joint.calc(zero)[0],
        "HEAD_OF_HOUSEHOLD": p.head_of_household.calc(zero)[0],
        "SEPARATE": p.separate.calc(zero)[0],
    }
    return result, cap


@pytest.mark.parametrize("year", [2020, 2021, 2025])
@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(units=st.lists(tax_unit(), min_size=6, max_size=6))
def test_or_federal_tax_liability_subtraction_invariants(year, units):
    result, cap = _run(units, year)
    for i, unit in enumerate(units):
        r = result[i]
        base, delta = r["base"], unit["delta"]
        # 1. Bounds.
        assert -TOLERANCE <= base
        assert base <= unit["income_tax_before_refundable_credits"] + TOLERANCE
        assert base <= cap[unit["filing_status"]] + TOLERANCE
        # 2. Credits the worksheet never lists.
        assert r["eitc"] == pytest.approx(base, abs=TOLERANCE)
        if year == 2021:
            assert base - delta - TOLERANCE <= r["refundable_ctc"] <= base + TOLERANCE
        else:
            assert r["refundable_ctc"] == pytest.approx(base, abs=TOLERANCE)
        # 3. A listed credit lowers the subtraction by at most its increase.
        assert base - delta - TOLERANCE <= r["assigned_aca_ptc"] <= base + TOLERANCE
        # 4. More federal tax raises it by at most the increase.
        assert base - TOLERANCE <= r["tax"] <= base + delta + TOLERANCE
