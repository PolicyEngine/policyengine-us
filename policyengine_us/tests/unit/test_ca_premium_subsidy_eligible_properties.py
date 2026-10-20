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

The model stores MAGI and the guideline as float32 and divides them in
float64, so the reference reads (d)(7) exactly on the stored float32 values.

- The parameters match the Designs' bounds and inclusivity.
- With every non-income condition met, eligibility equals the exact reading
  of (d)(7) for any stored income and guideline. The examples mix three kinds
  of income: whole dollars near each edge (some guidelines are multiples of
  $20, which put 165% and 200% on whole dollars); a few float32 steps either
  side of each edge; and incomes across the range. Some guidelines are
  fractional, like the projected ones.

Each example builds a fresh simulation, so nothing computed for one example
is cached into the next.
"""

from fractions import Fraction

import numpy as np
import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from policyengine_us import Simulation
from policyengine_us.system import system

# Program Design (d)(7), by plan year: (floor, limit, limit is inclusive).
DESIGN_BANDS = {
    # 2026 Design: "at or above 100 percent and at or below 165 percent".
    2026: (Fraction(1), Fraction(165, 100), True),
    # 2027 Design V4: "at or above 100 percent and under 200 percent".
    2027: (Fraction(1), Fraction(2), False),
}
EDGES = (Fraction(1), Fraction(165, 100), Fraction(2))
MAX_TAX_UNITS = 128


def stored(value):
    """The exact value of a number after float32 storage."""
    return Fraction(float(np.float32(value)))


def design_eligible(year, income, guideline):
    floor, limit, inclusive = DESIGN_BANDS[year]
    ratio = max(stored(income), 0) / stored(guideline)
    below_limit = ratio <= limit if inclusive else ratio < limit
    return ratio >= floor and below_limit


def model_eligible(year, incomes, guidelines):
    """Eligibility from a fresh simulation with every non-income condition met."""
    n = len(incomes)
    sim = Simulation(
        situation={
            "people": {f"p{i}": {"age": {year: 40}} for i in range(n)},
            "tax_units": {f"t{i}": {"members": [f"p{i}"]} for i in range(n)},
            "households": {
                f"h{i}": {"members": [f"p{i}"], "state_code": {year: "CA"}}
                for i in range(n)
            },
        }
    )
    sim.set_input("is_aca_ptc_eligible", year, np.ones(n, dtype=bool))
    sim.set_input("files_return_for_aca_ptc", year, np.ones(n, dtype=bool))
    sim.set_input("aca_magi", year, np.asarray(incomes, dtype=float))
    sim.set_input("tax_unit_fpg", year - 1, np.asarray(guidelines, dtype=float))
    return sim.calculate("ca_premium_subsidy_eligible", year)


def float32_steps(value, steps):
    """The float32 value `steps` representable numbers away from `value`."""
    x = np.float32(value)
    toward = np.float32(np.inf if steps > 0 else -np.inf)
    for _ in range(abs(steps)):
        x = np.nextafter(x, toward)
    return float(x)


@st.composite
def tax_unit_incomes(draw):
    guideline = draw(
        st.one_of(
            st.integers(10_000, 80_000).map(float),
            st.integers(500, 4_000).map(lambda k: 20.0 * k),
            st.floats(10_000, 500_000, width=32),
        )
    )
    edge_income = draw(st.sampled_from(EDGES)) * stored(guideline)
    kind = draw(st.sampled_from(["whole_dollars", "float32_steps", "any"]))
    if kind == "whole_dollars":
        income = float(int(edge_income) + draw(st.integers(-2, 2)))
    elif kind == "float32_steps":
        income = float32_steps(float(edge_income), draw(st.integers(-3, 3)))
    else:
        income = draw(st.floats(-50_000, float(np.float32(3 * guideline)), width=32))
    return income, guideline


@pytest.mark.parametrize("year", sorted(DESIGN_BANDS))
def test_parameters_match_program_design(year):
    p = system.parameters(f"{year}-01-01").gov.states.ca.hbex.premium_subsidy
    floor, limit, inclusive = DESIGN_BANDS[year]
    assert p.in_effect
    assert Fraction(str(p.fpl_floor)) == floor
    assert Fraction(str(p.fpl_limit)) == limit
    assert bool(p.fpl_limit_inclusive) is inclusive


@pytest.mark.parametrize("year", sorted(DESIGN_BANDS))
@settings(max_examples=30, deadline=None, derandomize=True)
@given(units=st.lists(tax_unit_incomes(), min_size=1, max_size=MAX_TAX_UNITS))
# PY2026, 2025 one-person guideline $15,650: 164.997%, 165.000%, 165.003%,
# 165.994% and 166.000%; truncation maps 165.000% to 165.994% to 1.65.
@example(
    units=[
        (25_822, 15_650),
        (25_822.5, 15_650),
        (25_823, 15_650),
        (25_978, 15_650),
        (25_979, 15_650),
    ]
)
# A $20-multiple guideline puts 100%, 165% and 200% on whole dollars.
@example(units=[(16_000, 16_000), (26_400, 16_000), (26_401, 16_000), (32_000, 16_000)])
# The 2025 guideline for 72 people, $406,150: $674,209 is exactly 166%, which
# float32 truncation in aca_magi_fraction misrounds to 165.99%.
@example(units=[(674_209, 406_150), (812_300, 406_150)])
# Stored float32 incomes a fraction of a cent above 165% of a fractional
# guideline: a float32 quotient rounds both ratios down to 1.65.
@example(units=[(18_711.599609375, 11_340.36328125), (37_907.703125, 22_974.365234375)])
def test_eligibility_matches_exact_program_design_band(year, units):
    incomes, guidelines = zip(*units)
    expected = [design_eligible(year, i, g) for i, g in units]
    actual = model_eligible(year, incomes, guidelines)
    mismatches = [
        (income, guideline, bool(a))
        for (income, guideline), a, e in zip(units, actual, expected)
        if bool(a) != e
    ]
    assert not mismatches
