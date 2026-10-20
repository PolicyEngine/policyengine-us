"""Properties of the California Premium Subsidy income band.

Program Design (d)(7) defines an applicable return filer by household income
"at or above 100 percent and at or below 165 percent of the federal poverty
level" in PY2026, and "at or above 100 percent and under 200 percent" in
PY2027. The bounds below are transcribed from those Designs, not read from
the parameters, and are evaluated in exact rational arithmetic.

The model divides nonnegative ACA MAGI by the prior-year poverty guideline.
It must not use aca_magi_fraction for the band: that fraction truncates to
whole percentages, so every income from 165.00% to 165.99% of the guideline
becomes 1.65 and would pass an "at or below 165 percent" test. FTB 3849
Table 1-2, for the predecessor California program, likewise truncates for
the rate lookup but decides band edges on the exact percentage.

- The parameters match the Designs' bounds and inclusivity.
- With every non-income condition met, eligibility equals the exact reading
  of (d)(7) for any income and guideline. Incomes are whole dollars, and some
  guidelines are multiples of $20, so 165% and 200% of the guideline are
  themselves whole dollars and the inclusive and strict edges are hit
  exactly.
"""

from fractions import Fraction

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation

# Program Design (d)(7), by plan year: (floor, limit, limit is inclusive).
DESIGN_BANDS = {
    # 2026 Design: "at or above 100 percent and at or below 165 percent".
    2026: (Fraction(1), Fraction(165, 100), True),
    # 2027 Design V4: "at or above 100 percent and under 200 percent".
    2027: (Fraction(1), Fraction(2), False),
}
EDGES = (Fraction(1), Fraction(165, 100), Fraction(2))
TAX_UNITS = 64


def design_eligible(year, income, guideline):
    floor, limit, inclusive = DESIGN_BANDS[year]
    ratio = Fraction(max(income, 0), guideline)
    below_limit = ratio <= limit if inclusive else ratio < limit
    return ratio >= floor and below_limit


@pytest.fixture(scope="module")
def simulations():
    """One simulation per plan year, with every non-income condition met."""
    sims = {}
    for year in DESIGN_BANDS:
        sim = Simulation(
            situation={
                "people": {f"p{i}": {"age": {year: 40}} for i in range(TAX_UNITS)},
                "tax_units": {
                    f"t{i}": {"members": [f"p{i}"]} for i in range(TAX_UNITS)
                },
                "households": {
                    f"h{i}": {"members": [f"p{i}"], "state_code": {year: "CA"}}
                    for i in range(TAX_UNITS)
                },
            }
        )
        sim.set_input("is_aca_ptc_eligible", year, np.ones(TAX_UNITS, dtype=bool))
        sim.set_input("files_return_for_aca_ptc", year, np.ones(TAX_UNITS, dtype=bool))
        sims[year] = sim
    return sims


def model_eligible(sim, year, incomes, guidelines):
    sim.set_input("aca_magi", year, np.asarray(incomes, dtype=float))
    sim.set_input("tax_unit_fpg", year - 1, np.asarray(guidelines, dtype=float))
    sim.delete_arrays("ca_premium_subsidy_eligible", year)
    return sim.calculate("ca_premium_subsidy_eligible", year)


@st.composite
def tax_unit_incomes(draw):
    """A whole-dollar income and guideline, often within $2 of a band edge."""
    guideline = draw(
        st.one_of(
            st.integers(10_000, 80_000),
            st.integers(500, 4_000).map(lambda k: 20 * k),
        )
    )
    edge = draw(st.sampled_from(EDGES))
    near_edge = int(edge * guideline) + draw(st.integers(-2, 2))
    income = draw(st.one_of(st.just(near_edge), st.integers(-50_000, 3 * guideline)))
    return income, guideline


@pytest.mark.parametrize("year", sorted(DESIGN_BANDS))
def test_parameters_match_program_design(year, simulations):
    p = (
        simulations[year]
        .tax_benefit_system.parameters(f"{year}-01-01")
        .gov.states.ca.hbex.premium_subsidy
    )
    floor, limit, inclusive = DESIGN_BANDS[year]
    assert p.in_effect
    assert Fraction(str(p.fpl_floor)) == floor
    assert Fraction(str(p.fpl_limit)) == limit
    assert bool(p.fpl_limit_inclusive) is inclusive


@pytest.mark.parametrize("year", sorted(DESIGN_BANDS))
@settings(max_examples=60, deadline=None, derandomize=True)
@given(units=st.lists(tax_unit_incomes(), min_size=1, max_size=TAX_UNITS))
# PY2026, 2025 one-person guideline $15,650: 165.000%, 165.003%, 165.994%
# and 166.000%; truncation maps the middle two to 1.65.
@example(units=[(25_822, 15_650), (25_823, 15_650), (25_978, 15_650), (25_979, 15_650)])
# A $20-multiple guideline puts 100%, 165% and 200% on whole dollars.
@example(units=[(16_000, 16_000), (26_400, 16_000), (26_401, 16_000), (32_000, 16_000)])
def test_eligibility_matches_exact_program_design_band(year, simulations, units):
    padded = (units * TAX_UNITS)[:TAX_UNITS]
    incomes, guidelines = zip(*padded)
    expected = [
        design_eligible(year, income, guideline) for income, guideline in padded
    ]
    actual = model_eligible(simulations[year], year, incomes, guidelines)
    mismatches = [
        (income, guideline, bool(a))
        for income, guideline, a, e in zip(incomes, guidelines, actual, expected)
        if bool(a) != e
    ]
    assert not mismatches
