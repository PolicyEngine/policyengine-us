"""The engine ages employer plan premium inputs by CMS's employer-sponsored
insurance premium per enrollee, in a simulation and in dataset extension.

``tests/core/test_esi_premium_uprating.py`` checks the series itself and that
both inputs name it. This file checks the distinct failure that a parameter
read cannot: that holder uprating in a ``Simulation`` and
``extend_single_year_dataset`` resolve the per-enrollee path undivided by
population (``tools/per_capita_uprating.py`` divides national totals) and
apply it to these inputs.

Invariants:

1. Uprating: a premium entered for 2024 equals that amount times the index
   ratio in any later year, for both inputs, so uprating is linear in the
   amount (Hypothesis, one vectorized simulation per example).
2. Dataset extension: each person's amount follows the index ratio, and the
   weighted total grows by the index ratio times population growth, because
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

ESI = "calibration.gov.hhs.cms.esi_premium_per_enrollee"
EMPLOYER, EMPLOYEE = (
    "employer_sponsored_insurance_premiums",
    "pre_tax_health_insurance_premiums",
)
BASE_YEAR, END_YEAR = 2024, 2100


def _ratio(path, year):
    parameter = get_parameter(system.parameters, path)
    return parameter(f"{year}-01-01") / parameter(f"{BASE_YEAR}-01-01")


# Each example builds one simulation holding a batch of people.
@settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)
@given(
    st.lists(
        st.tuples(
            st.integers(0, 5_000_000).map(lambda cents: cents / 100),
            st.integers(0, 2_000_000).map(lambda cents: cents / 100),
        ),
        min_size=2,
        max_size=8,
    ),
    st.lists(st.integers(BASE_YEAR + 1, END_YEAR), min_size=2, max_size=4),
)
def test_simulation_uprates_premiums_by_the_index_ratio(amounts, years):
    people = {
        f"person_{i}": {
            "age": {BASE_YEAR: 40},
            EMPLOYER: {BASE_YEAR: employer},
            EMPLOYEE: {BASE_YEAR: employee},
        }
        for i, (employer, employee) in enumerate(amounts)
    }
    simulation = Simulation(
        situation={
            "people": people,
            "households": {"household": {"members": list(people)}},
        }
    )
    for year in years:
        for column, variable in enumerate((EMPLOYER, EMPLOYEE)):
            values = simulation.calculate(variable, year)
            for value, pair in zip(values, amounts):
                assert value == pytest.approx(
                    pair[column] * _ratio(ESI, year), rel=1e-6, abs=0.01
                )


@lru_cache(maxsize=1)
def _extended():
    person = pd.DataFrame(
        {
            "person_id": [1, 2, 3, 4],
            "person_household_id": [1, 1, 2, 3],
            EMPLOYER: [14_000.0, 0.0, 6_500.0, 0.0],
            EMPLOYEE: [4_200.0, 0.0, 1_100.0, 900.0],
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


@pytest.mark.parametrize("year", [2025, 2030, 2034, 2036])
@pytest.mark.parametrize("variable", [EMPLOYER, EMPLOYEE])
def test_dataset_extension_uprates_by_the_index(variable, year):
    base, later = _extended().datasets[BASE_YEAR], _extended().datasets[year]
    for before, after in zip(base.person[variable], later.person[variable]):
        assert after == pytest.approx(before * _ratio(ESI, year), rel=1e-9)
    assert _weighted_total(later, variable) / _weighted_total(
        base, variable
    ) == pytest.approx(_ratio(ESI, year) * _ratio(POPULATION_PATH, year), rel=1e-9)
