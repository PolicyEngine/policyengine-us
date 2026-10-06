"""Invariants for the New York itemized medical expense deduction.

NY Tax Law 615(a) computes New York itemized deductions as federal deductions
existed immediately before Public Law 115-97, so Form IT-196 lines 1-4 keep
the 10% floor of pre-TCJA 26 USC 213(a): line 4 is medical and dental
expenses less 10% of federal AGI. The federal floor has been 7.5% since 2017.

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
   read from Form IT-196 line 3 rather than from the model's parameters.
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
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars
# The model stores float32, about 7 significant digits, so amounts in the
# hundreds of thousands also get a relative tolerance of a few float32 ulps.
RTOL = 1e-6

# Form IT-196 line 3, "Multiply line 2 by 10% (0.10)", on the 2018, 2021,
# 2024 and 2025 forms (tax.ny.gov/pdf/<year>/inc/it196_<year>_fill_in.pdf).
PUBLISHED_FLOOR = {2018: 0.1, 2021: 0.1, 2024: 0.1, 2025: 0.1}
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


def _slack(values):
    return TOLERANCE + RTOL * np.abs(values)


def _check(units, year):
    in_ny = np.array([unit["state"] == "NY" for unit in units])
    base = _run(units, year)
    expenses = base["itemized_medical_expenses"]
    deduction = base["ny_medical_expense_deduction"]

    # 1. Bounds, and zero outside New York.
    assert (deduction >= 0).all()
    assert (deduction <= expenses + _slack(expenses)).all()
    assert (deduction[~in_ny] == 0).all()

    # 2. Differential against numpy and the published floor.
    floor = PUBLISHED_FLOOR[year] * np.maximum(base["adjusted_gross_income"], 0)
    np.testing.assert_allclose(
        deduction[in_ny],
        np.maximum(expenses - floor, 0)[in_ny],
        atol=TOLERANCE,
        rtol=RTOL,
    )

    # 3. Never more than the federal deduction, whose floor is lower.
    federal = base["medical_expense_deduction"]
    assert (deduction <= federal + _slack(federal)).all()

    # 4. Monotone, and at most dollar for dollar, in expenses.
    raised = _run(units, year, raised=True)
    increase = raised["itemized_medical_expenses"] - expenses
    gain = raised["ny_medical_expense_deduction"] - deduction
    assert (gain >= -_slack(deduction)).all()
    assert (gain <= increase + _slack(raised["ny_medical_expense_deduction"])).all()

    # 5. Medical expenses reach the NY itemized total only through the NY
    # medical deduction.
    np.testing.assert_allclose(
        raised["ny_itemized_deductions_max"] - raised["ny_medical_expense_deduction"],
        base["ny_itemized_deductions_max"] - deduction,
        atol=TOLERANCE,
        rtol=RTOL,
    )

    # 6. The Line 40 limitation is unaffected by medical expenses.
    np.testing.assert_allclose(
        raised["ny_itemized_deductions_phase_out"],
        base["ny_itemized_deductions_phase_out"],
        atol=TOLERANCE,
        rtol=RTOL,
    )


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=8,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.sampled_from(YEARS), st.lists(tax_units(), min_size=5, max_size=30))
def test_ny_medical_expense_deduction_invariants(year, units):
    _check(units, year)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    _check(_seeded_units(), year)
