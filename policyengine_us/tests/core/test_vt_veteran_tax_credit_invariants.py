"""Invariants for Vermont's veteran tax credit, 32 V.S.A. § 5830g.

Under subsection (c), Vermont pays $250 on federal adjusted gross income (AGI)
of $25,000 or less, "$250.00 less $5.00 per $100.00" of AGI above $25,000
while AGI stays below $30,000, and nothing from $30,000. On the 2025
Schedule IN-112 (Part II, lines 8-12), filers count whole hundreds: line 10
has them divide the excess by 100, "rounding down to the nearest whole number".

`_worksheet` follows those lines with the dollar amounts typed from the statute
and the schedule, so it reads neither the parameters nor the formula. For every
tax unit:

1. Differential: a Vermont tax unit with a veteran gets the worksheet's amount
   from 2025, and every other tax unit gets zero. One simulation per year checks
   each whole-dollar AGI from $0 to $35,000. Hypothesis adds negative, large and
   fractional AGIs, joint units, units without a veteran, New Hampshire units
   and 2024, the year before the credit began.
2. Bounds: 0 <= credit <= $250.
3. Monotonicity: among Vermont units with a veteran, a higher AGI never brings
   a higher credit.
"""

import numpy as np
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

TOLERANCE = 0.001  # dollars

MAXIMUM_CREDIT = 250
FULL_CREDIT_AGI_LIMIT = 25_000
NO_CREDIT_AGI = 30_000
FIRST_YEAR = 2025
YEARS = (2024, 2025, 2026)


def _worksheet(agi):
    """2025 Schedule IN-112, Part II, lines 8-12, then § 5830g(c)(3)."""
    line_8 = np.asarray(agi, dtype=float)
    line_9 = np.where(
        line_8 <= FULL_CREDIT_AGI_LIMIT, 0, line_8 - FULL_CREDIT_AGI_LIMIT
    )
    line_10 = np.floor(line_9 / 100)
    line_11 = line_10 * 5
    line_12 = np.where(line_9 == 0, MAXIMUM_CREDIT, MAXIMUM_CREDIT - line_11)
    return np.where(line_8 >= NO_CREDIT_AGI, 0, line_12)


@pytest.mark.parametrize("year", [2025, 2026])
def test_vt_veteran_tax_credit_matches_worksheet_at_every_whole_dollar(year):
    top = 35_000
    sim = Simulation(
        situation={
            "people": {"veteran": {"is_veteran": {year: True}}},
            "tax_units": {"tax_unit": {"members": ["veteran"]}},
            "households": {
                "household": {"members": ["veteran"], "state_code": {year: "VT"}}
            },
            "axes": [
                [
                    {
                        "name": "adjusted_gross_income",
                        "min": 0,
                        "max": top,
                        "count": top + 1,
                        "period": year,
                    }
                ]
            ],
        }
    )
    agi = np.asarray(sim.calculate("adjusted_gross_income", year), dtype=float)
    credit = np.asarray(sim.calculate("vt_veteran_tax_credit", year), dtype=float)

    np.testing.assert_array_equal(agi, np.arange(top + 1))
    np.testing.assert_allclose(credit, _worksheet(agi), atol=TOLERANCE)

    # Each whole $100 above $25,000 takes $5, and the last $5 goes at $30,000.
    assert set(np.unique(credit)) == set(range(0, MAXIMUM_CREDIT + 1, 5))
    assert credit[29_999] == 5 and credit[30_000] == 0
    assert (np.diff(credit) <= 0).all()


agis = st.one_of(
    st.integers(-50_000, 60_000).map(float),
    st.integers(24_900, 30_100).map(float),
    st.integers(2_490_000, 3_010_000).map(lambda cents: cents / 100),
    st.sampled_from(
        [
            25_000.0,
            25_000.01,
            25_099.99,
            25_100.0,
            29_899.99,
            29_900.0,
            29_999.99,
            30_000.0,
        ]
    ),
)


@st.composite
def tax_units(draw):
    joint = draw(st.booleans())
    return {
        "agi": draw(agis),
        "state": draw(st.sampled_from(["VT", "VT", "VT", "NH"])),
        "veterans": [draw(st.booleans()) for _ in range(2 if joint else 1)],
    }


def _situation(units):
    # One simulation holds every year, so every_year keys each input by all of YEARS.
    def every_year(value):
        return {year: value for year in YEARS}

    people, tax_unit_inputs, households = {}, {}, {}
    for i, unit in enumerate(units):
        members = []
        for j, is_veteran in enumerate(unit["veterans"]):
            name = f"person_{i}_{j}"
            people[name] = {"age": every_year(40), "is_veteran": every_year(is_veteran)}
            members.append(name)
        tax_unit_inputs[f"tax_unit_{i}"] = {
            "members": members,
            "adjusted_gross_income": every_year(unit["agi"]),
        }
        households[f"household_{i}"] = {
            "members": members,
            "state_code": every_year(unit["state"]),
        }
    return {"people": people, "tax_units": tax_unit_inputs, "households": households}


def _check(units):
    sim = Simulation(situation=_situation(units))
    has_veteran = np.array([any(unit["veterans"]) for unit in units])
    in_vermont = np.array([unit["state"] == "VT" for unit in units])
    for year in YEARS:
        agi = np.asarray(sim.calculate("adjusted_gross_income", year), dtype=float)
        credit = np.asarray(sim.calculate("vt_veteran_tax_credit", year), dtype=float)
        qualifies = has_veteran & in_vermont & (year >= FIRST_YEAR)

        # 1. Differential against the worksheet.
        np.testing.assert_allclose(
            credit, np.where(qualifies, _worksheet(agi), 0), atol=TOLERANCE
        )

        # 2. Bounds.
        assert (credit >= 0).all()
        assert (credit <= MAXIMUM_CREDIT).all()

        # 3. Monotonicity in AGI among the units that qualify.
        by_agi = np.argsort(agi[qualifies], kind="stable")
        assert (np.diff(credit[qualifies][by_agi]) <= TOLERANCE).all()


@settings(
    max_examples=12,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.data_too_large],
)
@given(st.lists(tax_units(), min_size=1, max_size=20))
def test_vt_veteran_tax_credit_invariants(units):
    _check(units)
