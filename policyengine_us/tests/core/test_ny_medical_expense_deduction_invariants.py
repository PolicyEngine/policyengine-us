"""Invariants for the New York itemized medical expense deduction.

NY Tax Law 615(a) computes New York itemized deductions as federal deductions
existed immediately before Public Law 115-97, so Form IT-196 lines 1-4 keep
the 10% floor of pre-TCJA 26 USC 213(a): line 4 is medical and dental
expenses less 10% of federal AGI. The federal floor has been 7.5% since 2017.
Through 2017, Form IT-201-D line 1 took federal Schedule A line 4, so New
York followed the federal 7.5% floor in 2017.

Hypothesis draws batches of tax units (single or joint, in New York or
another state, with AGI from negative to several million, medical expenses,
real estate taxes and charitable gifts), and a seeded population of 200 units
adds breadth. Each batch runs as one vectorized simulation, and again with
every head's medical expenses raised by a drawn non-negative amount. For
every tax unit:

1. Bound: 0 <= ny_medical_expense_deduction <= itemized_medical_expenses,
   and it is zero outside New York.
2. Differential: in New York, ny_medical_expense_deduction equals an
   independent numpy max(0, expenses - floor * max(AGI, 0)), with the floor
   read from the forms (Form IT-196 line 3 from 2018; for 2017, the federal
   Schedule A line 3 that IT-201-D line 1 used) rather than from the model's
   parameters.
3. Order: it never exceeds the federal medical_expense_deduction.
4. Monotone: raising expenses by d raises it by at least 0 and at most d.
5. Composition: ny_itemized_deductions_max less ny_medical_expense_deduction
   does not change when medical expenses change.
6. Line 40: ny_itemized_deductions_phase_out does not change when medical
   expenses change, because the medical deduction enters worksheet line 1
   (deductions before the limitation) and line 2 (deductions not subject to
   it) alike.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
# The model computes in float32, about 7 significant digits. A difference of
# float32 amounts can be off by a few ulps of its largest operand (half an
# ulp is about 0.03 near 600,000) even when the result is near zero, so each
# comparison also allows RTOL times the largest amount that went into it.
RTOL = 1e-6

# Form IT-196 line 3, "Multiply line 2 by 10% (0.10)", on the 2018, 2021,
# 2024 and 2025 forms (tax.ny.gov/pdf/<year>/inc/it196_<year>_fill_in.pdf).
# For 2017, IT-201-D line 1 took federal Schedule A line 4, and the 2017
# Schedule A line 3 reads "Multiply line 2 by 7.5% (0.075)".
PUBLISHED_FLOOR = {2017: 0.075, 2018: 0.1, 2021: 0.1, 2024: 0.1, 2025: 0.1}
YEARS = sorted(PUBLISHED_FLOOR)
STATES = ["NY", "NY", "NY", "CA", "TX"]

agis = st.one_of(
    st.integers(-200_000, 0).map(float),
    st.integers(0, 500_000).map(float),
    st.integers(500_000, 6_000_000).map(float),
)
amounts = st.one_of(
    st.just(0.0),
    st.integers(1, 60_000).map(float),
    st.integers(60_000, 800_000).map(float),
)
increases = st.one_of(st.just(0.0), st.integers(1, 100_000).map(float))


@st.composite
def tax_units(draw):
    return {
        "joint": draw(st.booleans()),
        "state": draw(st.sampled_from(STATES)),
        "agi": draw(agis),
        "medical": draw(amounts),
        "real_estate_taxes": draw(amounts),
        "charity": draw(amounts),
        "increase": draw(increases),
    }


SEED = 20261006


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)

    def amount():
        return float(
            [0, rng.integers(1, 60_001), rng.integers(60_000, 800_001)][
                rng.choice([0, 1, 2])
            ]
        )

    return [
        {
            "joint": bool(rng.random() < 0.5),
            "state": str(rng.choice(STATES)),
            "agi": float(
                [
                    rng.integers(-200_000, 1),
                    rng.integers(0, 500_001),
                    rng.integers(500_000, 6_000_001),
                ][rng.choice([0, 1, 2])]
            ),
            "medical": amount(),
            "real_estate_taxes": amount(),
            "charity": amount(),
            "increase": float(rng.integers(0, 100_001)) if rng.random() < 0.7 else 0.0,
        }
        for _ in range(n)
    ]


def _situation(units, year, *, raised):
    people, groups = {}, {"tax_units": {}, "households": {}, "marital_units": {}}
    for i, unit in enumerate(units):
        head = f"head_{i}"
        people[head] = {
            "age": 45,
            "is_tax_unit_head": True,
            "other_medical_expenses": unit["medical"] + raised * unit["increase"],
            "real_estate_taxes": unit["real_estate_taxes"],
            "charitable_cash_donations": unit["charity"],
        }
        members = [head]
        if unit["joint"]:
            spouse = f"spouse_{i}"
            people[spouse] = {"age": 43, "is_tax_unit_spouse": True}
            members.append(spouse)
        groups["marital_units"][f"couple_{i}"] = {"members": members}
        groups["tax_units"][f"tax_unit_{i}"] = {
            "members": members,
            "adjusted_gross_income": {year: unit["agi"]},
        }
        groups["households"][f"household_{i}"] = {
            "members": members,
            "state_code": {year: unit["state"]},
        }
    people = {
        name: {key: {year: value} for key, value in values.items()}
        for name, values in people.items()
    }
    return {"people": people, **groups}


def _run(units, year, *, raised=False):
    sim = Simulation(situation=_situation(units, year, raised=raised))
    return {
        name: np.asarray(sim.calculate(name, year), dtype=float)
        for name in [
            "itemized_medical_expenses",
            "adjusted_gross_income",
            "medical_expense_deduction",
            "ny_medical_expense_deduction",
            "ny_itemized_deductions_max",
            "ny_itemized_deductions_phase_out",
        ]
    }


def _slack(*operands):
    return TOLERANCE + RTOL * np.max(np.abs(np.stack(operands)), axis=0)


def _assert_close(actual, desired, slack, what):
    off = np.abs(actual - desired) > slack
    assert not off.any(), f"{what}: {actual[off]} != {desired[off]}"


def _check(units, year):
    in_ny = np.array([unit["state"] == "NY" for unit in units])
    base = _run(units, year)
    expenses = base["itemized_medical_expenses"]
    deduction = base["ny_medical_expense_deduction"]

    agi = np.maximum(base["adjusted_gross_income"], 0)
    slack = _slack(expenses, agi)

    # 1. Bounds, and zero outside New York.
    assert (deduction >= 0).all()
    assert (deduction <= expenses + slack).all()
    assert (deduction[~in_ny] == 0).all()

    # 2. Differential against numpy and the published floor.
    expected = np.maximum(expenses - PUBLISHED_FLOOR[year] * agi, 0)
    _assert_close(deduction[in_ny], expected[in_ny], slack[in_ny], "differential")

    # 3. Never more than the federal deduction, whose floor is no higher.
    assert (deduction <= base["medical_expense_deduction"] + slack).all()

    # 4. Monotone, and at most dollar for dollar, in expenses.
    raised = _run(units, year, raised=True)
    raised_slack = _slack(raised["itemized_medical_expenses"], agi)
    increase = raised["itemized_medical_expenses"] - expenses
    gain = raised["ny_medical_expense_deduction"] - deduction
    assert (gain >= -raised_slack).all()
    assert (gain <= increase + raised_slack).all()

    # 5. Medical expenses reach the NY itemized total only through the NY
    # medical deduction.
    total_slack = _slack(
        raised["ny_itemized_deductions_max"], base["ny_itemized_deductions_max"]
    )
    _assert_close(
        raised["ny_itemized_deductions_max"] - raised["ny_medical_expense_deduction"],
        base["ny_itemized_deductions_max"] - deduction,
        total_slack,
        "composition",
    )

    # 6. The Line 40 limitation is unaffected by medical expenses.
    _assert_close(
        raised["ny_itemized_deductions_phase_out"],
        base["ny_itemized_deductions_phase_out"],
        total_slack,
        "Line 40",
    )


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


def _near_floor(agi, medical):
    return {
        "joint": False,
        "state": "NY",
        "agi": float(agi),
        "medical": float(medical),
        "real_estate_taxes": 0.0,
        "charity": 0.0,
        "increase": 0.0,
    }


@settings(**SETTINGS)
@given(st.sampled_from(YEARS), st.lists(tax_units(), min_size=5, max_size=30))
# Expenses within float32 rounding of a large floor, where a tolerance scaled
# by the result rather than the operands fails (review of #9931).
@example(2025, [_near_floor(5_999_999, 600_000)] * 5)
@example(2025, [_near_floor(5_999_997, 600_000), _near_floor(5_242_881, 524_290)])
def test_ny_medical_expense_deduction_invariants(year, units):
    _check(units, year)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    _check(_seeded_units(), year)
