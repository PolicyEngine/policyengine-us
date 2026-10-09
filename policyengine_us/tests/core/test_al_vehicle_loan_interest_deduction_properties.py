"""Invariants for Alabama's qualified vehicle loan interest deduction.

Ala. Code 40-18-15(a)(2) allows interest to the extent 26 U.S.C. 163 allows
it, which from 2025 through 2028 includes qualified passenger vehicle loan
interest under 163(h)(4). The Department of Revenue's Qualified Vehicle Loan
Interest Worksheet (2025 Form 40 instructions, PDF page 31) takes the smaller
of the interest and $10,000, less $200 for each $1,000 (or part) of Alabama
AGI over $100,000 ($200,000 if married filing jointly). The result goes on
Schedule A line 11c, so it counts only when the filer itemizes.

Hypothesis draws batches of one-person tax units in Alabama or Georgia with
wages, Social Security (in federal AGI but not Alabama AGI), real estate tax,
qualified vehicle loan interest and a filing status, and a seeded population
of 200 units adds breadth. Each batch runs as one vectorized simulation, again
with interest raised and wages raised, and again with no interest. For every
tax unit:

1. Bound: 0 <= al_vehicle_loan_interest_deduction <= min(interest, $10,000),
   and it is 0 outside Alabama.
2. Differential (worksheet): it equals an independent numpy statement of the
   worksheet, with the dollar amounts typed from the worksheet rather than
   read from the model's parameters, and with Alabama AGI as line 3.
3. Differential (federal): where Alabama AGI equals federal modified AGI, it
   equals the federal auto_loan_interest_deduction, which states the same
   163(h)(4) limits.
4. Monotone: more interest never lowers it; more wages never raise it.
5. Accounting: al_itemized_deductions less al_itemized_deductions with no
   interest equals the deduction in 2025 through 2028 and is 0 in 2024 and
   2029.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.01  # dollars

# Worksheet lines 2, 4, 6 and 7.
CAP = 10_000
THRESHOLD_JOINT = 200_000
THRESHOLD_OTHER = 100_000
STEP = 1_000
REDUCTION_PER_STEP = 200
# 163(h)(4)(A): taxable years beginning after December 31, 2024, and before
# January 1, 2029.
ALLOWED_YEARS = {2025, 2026, 2027, 2028}
YEARS = [2024, 2025, 2026, 2027, 2028, 2029]

STATUSES = ["SINGLE", "JOINT", "SEPARATE", "HEAD_OF_HOUSEHOLD", "SURVIVING_SPOUSE"]

# Mostly incomes near the thresholds, plus zeros and large amounts.
wages = st.one_of(
    st.just(0.0),
    st.integers(1, 90_000).map(float),
    st.integers(90_000, 260_000).map(float),
    st.integers(260_000, 400_000).map(float),
)
social_security = st.one_of(st.just(0.0), st.integers(1, 60_000).map(float))
interest = st.one_of(
    st.just(0.0),
    st.integers(1, 10_000).map(float),
    st.integers(10_000, 20_000).map(float),
)
increases = st.one_of(st.just(0.0), st.integers(1, 5_000).map(float))


@st.composite
def tax_units(draw):
    return {
        "state_code": draw(st.sampled_from(["AL", "AL", "AL", "GA"])),
        "filing_status": draw(st.sampled_from(STATUSES)),
        "employment_income": draw(wages),
        "social_security_retirement": draw(social_security),
        "real_estate_taxes": draw(st.integers(0, 8_000).map(float)),
        "interest": draw(interest),
        "interest_increase": draw(increases),
        "wage_increase": draw(increases),
    }


SEED = 20261009


def _seeded_units(n=200):
    rng = np.random.default_rng(SEED)
    units = []
    for _ in range(n):
        band = rng.integers(0, 4)
        wage = [
            0,
            rng.integers(1, 90_001),
            rng.integers(90_000, 260_001),
            rng.integers(260_000, 400_001),
        ][band]
        units.append(
            {
                "state_code": "GA" if rng.random() < 0.2 else "AL",
                "filing_status": str(rng.choice(STATUSES)),
                "employment_income": float(wage),
                "social_security_retirement": (
                    float(rng.integers(1, 60_001)) if rng.random() < 0.3 else 0.0
                ),
                "real_estate_taxes": float(rng.integers(0, 8_001)),
                "interest": float(
                    [0, rng.integers(1, 10_001), rng.integers(10_000, 20_001)][
                        rng.integers(0, 3)
                    ]
                ),
                "interest_increase": float(rng.integers(0, 5_001)),
                "wage_increase": float(rng.integers(0, 5_001)),
            }
        )
    return units


def _situation(units, year, *, interest_scale, raise_interest, raise_wages):
    people, tax_units_, households, marital_units = {}, {}, {}, {}
    for i, unit in enumerate(units):
        name = f"person_{i}"
        people[name] = {
            "age": {year: 50},
            "employment_income": {
                year: unit["employment_income"] + raise_wages * unit["wage_increase"]
            },
            "social_security_retirement": {year: unit["social_security_retirement"]},
            "real_estate_taxes": {year: unit["real_estate_taxes"]},
        }
        tax_units_[f"tax_unit_{i}"] = {
            "members": [name],
            "filing_status": {year: unit["filing_status"]},
        }
        marital_units[f"marital_unit_{i}"] = {"members": [name]}
        households[f"household_{i}"] = {
            "members": [name],
            "state_code": {year: unit["state_code"]},
            "qualified_passenger_vehicle_loan_interest": {
                year: interest_scale
                * (unit["interest"] + raise_interest * unit["interest_increase"])
            },
        }
    return {
        "people": people,
        "tax_units": tax_units_,
        "marital_units": marital_units,
        "households": households,
    }


VARIABLES = [
    "al_vehicle_loan_interest_deduction",
    "al_itemized_deductions",
    "al_agi",
    "agi_plus_section_911_931_933_exclusions",
    "auto_loan_interest_deduction",
]


def _run(units, year, *, interest_scale=1, raise_interest=False, raise_wages=False):
    sim = Simulation(
        situation=_situation(
            units,
            year,
            interest_scale=interest_scale,
            raise_interest=raise_interest,
            raise_wages=raise_wages,
        )
    )
    return {
        name: np.asarray(sim.calculate(name, year), dtype=float) for name in VARIABLES
    }


def _worksheet(interest, al_agi, joint):
    line_2 = np.minimum(interest, CAP)
    line_4 = np.where(joint, THRESHOLD_JOINT, THRESHOLD_OTHER)
    line_5 = np.maximum(al_agi - line_4, 0)
    line_6 = np.ceil(line_5 / STEP)
    line_7 = line_6 * REDUCTION_PER_STEP
    return np.maximum(line_2 - line_7, 0)


def _check(units, year):
    alabama = np.array([u["state_code"] == "AL" for u in units])
    joint = np.array([u["filing_status"] == "JOINT" for u in units])
    interest = np.array([u["interest"] for u in units])
    raised_interest = interest + np.array([u["interest_increase"] for u in units])

    base = _run(units, year)
    deduction = base["al_vehicle_loan_interest_deduction"]

    # 1. Bounds.
    assert (deduction >= 0).all()
    assert (deduction <= np.minimum(interest, CAP) + TOLERANCE).all()
    assert (deduction[~alabama] == 0).all()

    # 2. Differential against the worksheet.
    expected = np.where(alabama, _worksheet(interest, base["al_agi"], joint), 0)
    np.testing.assert_allclose(deduction, expected, atol=TOLERANCE)

    # 3. Differential against the federal deduction where the incomes agree.
    same_income = alabama & (
        np.abs(base["al_agi"] - base["agi_plus_section_911_931_933_exclusions"])
        < TOLERANCE
    )
    np.testing.assert_allclose(
        deduction[same_income],
        base["auto_loan_interest_deduction"][same_income],
        atol=TOLERANCE,
    )

    # 4. Monotone in interest and in wages.
    more_interest = _run(units, year, raise_interest=True)
    assert (
        more_interest["al_vehicle_loan_interest_deduction"] >= deduction - TOLERANCE
    ).all()
    np.testing.assert_allclose(
        more_interest["al_vehicle_loan_interest_deduction"],
        np.where(alabama, _worksheet(raised_interest, base["al_agi"], joint), 0),
        atol=TOLERANCE,
    )
    more_wages = _run(units, year, raise_wages=True)
    assert (
        more_wages["al_vehicle_loan_interest_deduction"] <= deduction + TOLERANCE
    ).all()

    # 5. Itemized only in 2025 through 2028.
    no_interest = _run(units, year, interest_scale=0)
    added = base["al_itemized_deductions"] - no_interest["al_itemized_deductions"]
    if year in ALLOWED_YEARS:
        np.testing.assert_allclose(added, deduction, atol=TOLERANCE)
    else:
        np.testing.assert_allclose(added, 0, atol=TOLERANCE)


# A batch's cost is mostly per-variable overhead, so each example is a large
# batch and there are few examples.
SETTINGS = dict(
    max_examples=6,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)


@settings(**SETTINGS)
@given(st.sampled_from(YEARS), st.lists(tax_units(), min_size=5, max_size=30))
def test_al_vehicle_loan_interest_deduction_invariants(year, units):
    _check(units, year)


@pytest.mark.parametrize("year", YEARS)
def test_seeded_population(year):
    _check(_seeded_units(), year)
