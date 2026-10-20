"""Properties of the premium tax credit income test.

26 U.S.C. 36B(c)(1)(A) makes an applicable taxpayer one whose household
income "equals or exceeds 100 percent but does not exceed 400 percent" of the
poverty line. 36B(c)(1)(E) removed the 400% ceiling for 2021 through 2025.
The bands below are transcribed from the statute, not read from the
parameters, and are evaluated in exact rational arithmetic on the values the
model receives (ACA MAGI and the guideline are stored as float32).

aca_magi_fraction drops the decimals of the percentage, as Form 8962 line 5
does, so every income from 400.00% to 400.99% of the guideline becomes 4.00.
Form 8962 Worksheet 2 first decides "more than 400%" on the dollar amounts.

- The income scale's thresholds and amounts match the statute.
- For any income and guideline, aca_ptc_income_eligible equals the exact
  reading of 36B(c)(1)(A). Incomes are whole dollars or cents near an edge,
  so income exactly at 100% and 400% of the guideline is hit.
"""

from fractions import Fraction

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

# Tax year: (floor, ceiling or None when 36B(c)(1)(E) removes it).
STATUTE_BANDS = {
    2025: (Fraction(1), None),
    2026: (Fraction(1), Fraction(4)),
    2027: (Fraction(1), Fraction(4)),
}
EDGES = (Fraction(1), Fraction(4))
TAX_UNITS = 64


def as_received(value):
    """The exact value of a number after float32 storage."""
    return Fraction(float(np.float32(value)))


def statute_eligible(year, income, guideline):
    floor, ceiling = STATUTE_BANDS[year]
    ratio = max(as_received(income), 0) / as_received(guideline)
    return ratio >= floor and (ceiling is None or ratio <= ceiling)


@pytest.fixture(scope="module")
def simulations():
    sims = {}
    for year in STATUTE_BANDS:
        sims[year] = Simulation(
            situation={
                "people": {f"p{i}": {"age": {year: 40}} for i in range(TAX_UNITS)},
                "tax_units": {
                    f"t{i}": {"members": [f"p{i}"]} for i in range(TAX_UNITS)
                },
                "households": {
                    f"h{i}": {"members": [f"p{i}"], "state_code": {year: "TX"}}
                    for i in range(TAX_UNITS)
                },
            }
        )
    return sims


def model_eligible(sim, year, incomes, guidelines):
    sim.set_input("aca_magi", year, np.asarray(incomes, dtype=float))
    sim.set_input("tax_unit_fpg", year - 1, np.asarray(guidelines, dtype=float))
    for variable in ("aca_magi_fraction", "aca_ptc_income_eligible"):
        sim.delete_arrays(variable, year)
    return sim.calculate("aca_ptc_income_eligible", year)


@st.composite
def tax_unit_incomes(draw):
    """An income and guideline, often within $2 (in cents) of an edge."""
    guideline = draw(
        st.one_of(
            st.integers(10_000, 80_000),
            st.integers(500, 4_000).map(lambda k: 20 * k),
        )
    )
    edge = draw(st.sampled_from(EDGES))
    near_edge = (int(edge * guideline) * 100 + draw(st.integers(-200, 200))) / 100
    income = draw(
        st.one_of(
            st.just(near_edge),
            st.integers(-50_000, 5 * guideline).map(float),
        )
    )
    return income, guideline


@pytest.mark.parametrize("year", sorted(STATUTE_BANDS))
def test_scale_matches_statute(year, simulations):
    scale = (
        simulations[year]
        .tax_benefit_system.parameters(f"{year}-01-01")
        .gov.aca.ptc_income_eligibility
    )
    floor, ceiling = STATUTE_BANDS[year]
    assert [Fraction(str(t)) for t in scale.thresholds] == [0, floor, Fraction(4)]
    assert [bool(a) for a in scale.amounts] == [False, True, ceiling is None]


@pytest.mark.parametrize("year", sorted(STATUTE_BANDS))
@settings(max_examples=60, deadline=None, derandomize=True)
@given(units=st.lists(tax_unit_incomes(), min_size=1, max_size=TAX_UNITS))
# 2025 one-person guideline $15,650: 99.994%, 100%, 399.994%, exactly 400%,
# 400.003% and 400.994%. Truncation maps the last three to 4.00.
@example(
    units=[
        (15_649.0, 15_650),
        (15_650.0, 15_650),
        (62_599.0, 15_650),
        (62_600.0, 15_650),
        (62_600.47, 15_650),
        (62_755.56, 15_650),
    ]
)
def test_income_test_matches_statute(year, simulations, units):
    padded = (units * TAX_UNITS)[:TAX_UNITS]
    incomes, guidelines = zip(*padded)
    expected = [statute_eligible(year, income, g) for income, g in padded]
    actual = model_eligible(simulations[year], year, incomes, guidelines)
    mismatches = [
        (income, g, bool(a))
        for income, g, a, e in zip(incomes, guidelines, actual, expected)
        if bool(a) != e
    ]
    assert not mismatches
