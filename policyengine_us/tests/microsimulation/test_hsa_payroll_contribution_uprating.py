"""The engine ages HSA payroll contributions by the 26 U.S.C. 223(b)(2)
family contribution limit, in a simulation and in dataset extension.

``tests/core/test_hsa_contribution_limits.py`` checks the limits themselves
and ``tests/core/test_uprating_series.py`` that the input names the family
limit. This file checks what a parameter read cannot: that holder uprating in
a ``Simulation`` and ``extend_single_year_dataset`` resolve the path
undivided by population (``tools/per_capita_uprating.py`` divides only
national totals) and apply it to this input.

Invariants:

1. Uprating: a contribution entered for 2024 equals that amount times the
   ratio of the family limit in any later year, so uprating is linear in the
   amount (Hypothesis, one vectorized simulation per example). The uprated
   amount is what the payroll exclusion subtracts from wages.
2. Bound: a contribution at the 2024 family limit equals the family limit in
   every later year, and one at the 2024 self-only limit stays within $25 of
   the self-only limit, so uprating never carries a contribution at the cap
   past it.
3. Dataset extension: each person's amount follows the limit ratio, and the
   weighted total grows by the limit ratio times population growth, because
   weights follow population.
"""

from functools import lru_cache

import pandas as pd
import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from policyengine_core.parameters.operations.get_parameter import get_parameter

from policyengine_us import Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.data.economic_assumptions import extend_single_year_dataset
from policyengine_us.system import system
from policyengine_us.tools.per_capita_uprating import POPULATION_PATH

HSA = "health_savings_account_payroll_contributions"
LIMIT = "gov.irs.gross_income.health_savings_account_contributions.limit"
FAMILY, SELF_ONLY = f"{LIMIT}.family", f"{LIMIT}.self_only"
BASE_YEAR, END_YEAR = 2024, 2100


def _value(path, year):
    return get_parameter(system.parameters, path)(f"{year}-01-01")


def _ratio(path, year):
    return _value(path, year) / _value(path, BASE_YEAR)


def _simulation(amounts):
    people = {
        f"person_{i}": {"age": {BASE_YEAR: 40}, HSA: {BASE_YEAR: amount}}
        for i, amount in enumerate(amounts)
    }
    return Simulation(
        situation={
            "people": people,
            "households": {"household": {"members": list(people)}},
        }
    )


# Each example builds one simulation holding a batch of people.
@settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    st.lists(
        st.integers(0, 2_000_000).map(lambda cents: cents / 100),
        min_size=2,
        max_size=8,
    ),
    st.lists(st.integers(BASE_YEAR + 1, END_YEAR), min_size=2, max_size=4),
)
def test_simulation_uprates_contributions_by_the_family_limit(amounts, years):
    simulation = _simulation(amounts)
    for year in years:
        values = simulation.calculate(HSA, year)
        excluded = simulation.calculate("pre_tax_contributions", year)
        for value, exclusion, amount in zip(values, excluded, amounts):
            assert value == pytest.approx(
                amount * _ratio(FAMILY, year), rel=1e-6, abs=0.01
            )
            # HSA contributions are the only pre-tax payroll deduction here.
            assert exclusion == pytest.approx(value, rel=1e-6, abs=0.01)


@pytest.mark.parametrize("year", [2025, 2026, 2027, 2030, 2034, 2050, 2100])
def test_contributions_at_the_limit_stay_at_the_limit(year):
    family, self_only = _value(FAMILY, BASE_YEAR), _value(SELF_ONLY, BASE_YEAR)
    values = _simulation([family, self_only]).calculate(HSA, year)
    assert values[0] == pytest.approx(_value(FAMILY, year), abs=0.01)
    assert abs(values[1] - _value(SELF_ONLY, year)) <= 25 + 0.01


@lru_cache(maxsize=1)
def _extended():
    person = pd.DataFrame(
        {
            "person_id": [1, 2, 3, 4],
            "person_household_id": [1, 1, 2, 3],
            HSA: [8_300.0, 0.0, 4_150.0, 1_200.0],
            "age": [40.0, 8.0, 55.0, 62.0],
        }
    )
    household = pd.DataFrame(
        {"household_id": [1, 2, 3], "household_weight": [1_000.0, 2_500.0, 400.0]}
    )
    dataset = USSingleYearDataset(
        person=person,
        household=household,
        tax_unit=pd.DataFrame({"tax_unit_id": [1, 2, 3]}),
        spm_unit=pd.DataFrame({"spm_unit_id": [1, 2, 3]}),
        family=pd.DataFrame({"family_id": [1, 2, 3]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [1, 2, 3, 4]}),
        time_period=BASE_YEAR,
    )
    return extend_single_year_dataset(dataset, end_year=2036, system=system)


def _weighted_total(dataset, column):
    weights = dataset.household.set_index("household_id")["household_weight"]
    person_weights = dataset.person["person_household_id"].map(weights)
    return float((dataset.person[column] * person_weights).sum())


@pytest.mark.parametrize("year", [2025, 2027, 2030, 2034, 2036])
def test_dataset_extension_uprates_by_the_family_limit(year):
    base, later = _extended().datasets[BASE_YEAR], _extended().datasets[year]
    for before, after in zip(base.person[HSA], later.person[HSA]):
        assert after == pytest.approx(before * _ratio(FAMILY, year), rel=1e-9)
    assert _weighted_total(later, HSA) / _weighted_total(base, HSA) == pytest.approx(
        _ratio(FAMILY, year) * _ratio(POPULATION_PATH, year), rel=1e-9
    )
