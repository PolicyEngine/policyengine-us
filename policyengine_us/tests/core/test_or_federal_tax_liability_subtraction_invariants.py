"""Oregon's federal tax liability subtraction follows the OR-17 worksheet.

ORS 316.680(1)(b) and 316.685; Publication OR-17, federal tax worksheet,
Part A. The subtraction is federal tax after nonrefundable credits plus other
income taxes, less only the refundable credits the worksheet lists, floored at
zero and capped by a schedule that falls with federal AGI. With T the federal
tax before refundable credits, these properties hold for every input:

1. 0 <= subtraction <= min(max(0, T - NIIT - unreported payroll tax), cap(AGI)): the
   worksheet leaves out those two taxes, and the cap binds at the unit's AGI.
2. The earned income credit never changes it (ORS 316.685(1)(b)), and outside
   2021 neither does the additional child tax credit.
3. While the cap does not bind, raising a listed credit by d lowers it to
   exactly max(0, subtraction - d): the premium tax credit every year, and the
   refundable child tax credit and child care credit in 2021.
4. Raising T by d raises it by at most d, and never lowers it.

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
VARIANTS = ("base", "eitc", "refundable_ctc", "assigned_aca_ptc", "cdcc", "tax")


@st.composite
def tax_unit(draw):
    return {
        "filing_status": draw(st.sampled_from(FILING_STATUSES)),
        "adjusted_gross_income": draw(st.integers(0, 200_000)),
        "income_tax_before_refundable_credits": draw(st.integers(0, 20_000)),
        "net_investment_income_tax": draw(st.integers(0, 2_000)),
        "unreported_payroll_tax": draw(st.integers(0, 1_000)),
        **{credit: draw(st.integers(0, 3_000)) for credit in CREDITS},
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
    # Each unit's cap at its own AGI, from the simulation's own parameters.
    p = (
        simulation.tax_benefit_system.parameters(f"{year}-01-01")
        .gov.states["or"]
        .tax.income.subtractions.federal_tax_liability.cap
    )
    schedules = {
        "SINGLE": p.single,
        "JOINT": p.joint,
        "HEAD_OF_HOUSEHOLD": p.head_of_household,
        "SEPARATE": p.separate,
    }
    caps = [
        float(
            schedules[unit["filing_status"]].calc(
                np.array([float(unit["adjusted_gross_income"])])
            )[0]
        )
        for unit in units
    ]
    return result, caps


@pytest.mark.parametrize("year", [2020, 2021, 2025])
@settings(
    max_examples=4,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(units=st.lists(tax_unit(), min_size=6, max_size=6))
def test_or_federal_tax_liability_subtraction_invariants(year, units):
    result, caps = _run(units, year)
    for i, unit in enumerate(units):
        r = result[i]
        base, delta, cap = r["base"], unit["delta"], caps[i]
        uncapped = cap - base > TOLERANCE
        # 1. Bounds.
        assert -TOLERANCE <= base
        assert base <= TOLERANCE + max(
            0,
            unit["income_tax_before_refundable_credits"]
            - unit["net_investment_income_tax"]
            - unit["unreported_payroll_tax"],
        )
        assert base <= cap + TOLERANCE
        # 2. Credits the worksheet never lists.
        assert r["eitc"] == pytest.approx(base, abs=TOLERANCE)
        if year != 2021:
            assert r["refundable_ctc"] == pytest.approx(base, abs=TOLERANCE)
        # 3. A listed credit lowers the subtraction dollar for dollar to zero.
        listed = ["assigned_aca_ptc"]
        if year == 2021:
            listed += ["refundable_ctc", "cdcc"]
        for credit in listed:
            assert r[credit] <= base + TOLERANCE
            if uncapped:
                assert r[credit] == pytest.approx(max(0.0, base - delta), abs=TOLERANCE)
        # 4. More federal tax raises it by at most the increase.
        assert base - TOLERANCE <= r["tax"] <= base + delta + TOLERANCE
