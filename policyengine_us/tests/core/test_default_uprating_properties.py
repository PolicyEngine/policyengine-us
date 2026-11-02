"""Property tests: dollar inputs that follow the default uprating series.

Inputs with no series of their own follow
calibration.gov.cbo.income_by_source.adjusted_gross_income_per_capita, total
AGI divided by population. Total AGI is IRS SOI Publication 1304 Table 1.1
(all returns, adjusted gross income less deficit) for 2015 to 2018 and CBO's
series from 2019.

1. An input dated year X and read in a later year Y equals the input times
   index(Y) / index(X), for any pair of years from 2015 to 2036, and that one
   factor applies to every household. Reason: every projected input on the
   default series rests on it, and test_simulation_uprating_tracks_national_
   totals checks it only from 2024, for the SOI employment series.
2. The index never moves more than 25% from one year to the next. Reason: a
   year with no value holds the year before, so the per-capita index drifts
   down with population and jumps when values resume. Missing 2016 to 2018
   made 2018 to 2019 a 31.7% jump; with every year filled, the largest move is
   16.5%, from 2020 to 2021.
"""

import hypothesis
import pytest
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us import Simulation
from policyengine_us.system import system

DEFAULT = "calibration.gov.cbo.income_by_source.adjusted_gross_income_per_capita"
# A dollar input with no formula and no series of its own.
INPUT = "charitable_cash_donations"
FIRST_YEAR = 2015
LAST_YEAR = 2036
MAX_ANNUAL_MOVE = 0.25


def _index(year):
    return get_parameter(system.parameters, DEFAULT)(f"{year}-01-01")


def test_the_input_follows_the_default_series():
    assert system.variables[INPUT].uprating == DEFAULT


@hypothesis.settings(max_examples=15, deadline=None, derandomize=True)
@hypothesis.given(
    years=st.lists(
        st.integers(FIRST_YEAR, LAST_YEAR), min_size=2, max_size=2, unique=True
    ).map(sorted),
    amounts=st.lists(
        st.floats(0, 10_000_000, allow_nan=False, allow_infinity=False),
        min_size=1,
        max_size=4,
    ),
)
def test_an_input_grows_by_the_ratio_of_the_index(years, amounts):
    dated, read = years
    simulation = Simulation(
        situation={
            "people": {
                f"person_{i}": {INPUT: {dated: amount}}
                for i, amount in enumerate(amounts)
            },
            "households": {
                f"household_{i}": {"members": [f"person_{i}"]}
                for i in range(len(amounts))
            },
        }
    )
    factor = _index(read) / _index(dated)
    projected = simulation.calculate(INPUT, read)
    # Inputs are stored as float32.
    assert projected.tolist() == pytest.approx(
        [amount * factor for amount in amounts], rel=1e-6, abs=1e-3
    )


@pytest.mark.parametrize("year", range(FIRST_YEAR + 1, LAST_YEAR + 1))
def test_the_index_moves_less_than_a_quarter_in_a_year(year):
    move = _index(year) / _index(year - 1) - 1
    assert abs(move) < MAX_ANNUAL_MOVE, f"{year - 1} to {year}: {move:+.1%}"
