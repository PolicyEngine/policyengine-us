"""The engine ages premium inputs by their premium series, in a simulation and
in dataset extension.

``tests/core/test_premium_input_uprating.py`` checks the series and that each
input names its series. This file checks what a parameter read cannot: that
holder uprating in a ``Simulation`` and ``extend_single_year_dataset`` resolve
the per-enrollee paths and the price index undivided by population and apply
them to these inputs.

Invariants:

1. Uprating: a premium entered for 2024 equals that amount times its index
   ratio in any later year, so uprating is linear in the amount (Hypothesis,
   one vectorized simulation per example).
2. Move neutrality: splitting an employee's premium in any proportion between
   the pre-tax input and the reported premium inputs leaves the uprated total
   unchanged in every later year (Hypothesis). This is what Microcosm's
   pre-tax producer does when it routes a reported premium through payroll.
3. Dataset extension: each person's amount follows the index ratio, and the
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
DIRECT_PURCHASE = "calibration.gov.hhs.cms.direct_purchase_premium_per_enrollee"
MEDICAL_CPI = "gov.bls.cpi.cpi_u_medical_care"
PART_B = "calibration.gov.hhs.cms.medicare_part_b_premium_per_enrollee"
PRE_TAX = "pre_tax_health_insurance_premiums"
REPORTED = "health_insurance_premiums_without_medicare_part_b"
OTHER = "other_health_insurance_premiums"
DIRECT = "health_insurance_premiums"
LONG_TERM_CARE = "long_term_health_insurance_premiums"
PART_B_REPORTED = "medicare_part_b_premiums_reported"
SERIES = {
    PRE_TAX: ESI,
    REPORTED: ESI,
    OTHER: ESI,
    DIRECT: DIRECT_PURCHASE,
    LONG_TERM_CARE: MEDICAL_CPI,
    PART_B_REPORTED: PART_B,
}
BASE_YEAR, END_YEAR = 2024, 2100

amounts = st.integers(0, 3_000_000).map(lambda cents: cents / 100)
later_years = st.lists(st.integers(BASE_YEAR + 1, END_YEAR), min_size=2, max_size=4)
SETTINGS = settings(
    max_examples=3,
    deadline=None,
    derandomize=True,
    suppress_health_check=[HealthCheck.too_slow],
)


def _ratio(path, year):
    parameter = get_parameter(system.parameters, path)
    return parameter(f"{year}-01-01") / parameter(f"{BASE_YEAR}-01-01")


def _simulation(people):
    return Simulation(
        situation={
            "people": people,
            "households": {"household": {"members": list(people)}},
        }
    )


# Each example builds one simulation holding a batch of people.
@SETTINGS
@given(
    st.lists(st.tuples(*(amounts,) * len(SERIES)), min_size=2, max_size=6),
    later_years,
)
def test_simulation_uprates_premiums_by_their_index_ratio(rows, years):
    people = {
        f"person_{i}": {
            "age": {BASE_YEAR: 40},
            **{variable: {BASE_YEAR: amount} for variable, amount in zip(SERIES, row)},
        }
        for i, row in enumerate(rows)
    }
    simulation = _simulation(people)
    for year in years:
        for column, (variable, series) in enumerate(SERIES.items()):
            values = simulation.calculate(variable, year)
            for value, row in zip(values, rows):
                assert value == pytest.approx(
                    row[column] * _ratio(series, year), rel=1e-6, abs=0.01
                )


@SETTINGS
@given(
    st.lists(
        st.tuples(amounts, st.integers(0, 100), st.sampled_from((REPORTED, OTHER))),
        min_size=2,
        max_size=6,
    ),
    later_years,
)
def test_moving_a_premium_to_pre_tax_keeps_its_growth(rows, years):
    """Each person's premium is split: ``percent`` of it pre-tax, the rest in
    a reported premium input. Their uprated sum equals the whole premium
    uprated, whatever the split."""
    people = {}
    for i, (amount, percent, reported) in enumerate(rows):
        pre_tax = amount * percent / 100
        people[f"person_{i}"] = {
            "age": {BASE_YEAR: 40},
            PRE_TAX: {BASE_YEAR: pre_tax},
            reported: {BASE_YEAR: amount - pre_tax},
        }
    simulation = _simulation(people)
    for year in years:
        totals = (
            simulation.calculate(PRE_TAX, year)
            + simulation.calculate(REPORTED, year)
            + simulation.calculate(OTHER, year)
        )
        for total, (amount, _, _) in zip(totals, rows):
            assert total == pytest.approx(
                amount * _ratio(ESI, year), rel=1e-6, abs=0.01
            )


@lru_cache(maxsize=1)
def _extended():
    person = pd.DataFrame(
        {
            "person_id": [1, 2, 3, 4],
            "person_household_id": [1, 1, 2, 3],
            PRE_TAX: [3_100.0, 0.0, 1_200.0, 0.0],
            REPORTED: [1_400.0, 0.0, 6_300.0, 2_250.0],
            OTHER: [1_400.0, 0.0, 5_100.0, 2_250.0],
            DIRECT: [0.0, 0.0, 6_300.0, 0.0],
            LONG_TERM_CARE: [0.0, 0.0, 0.0, 3_100.0],
            PART_B_REPORTED: [0.0, 0.0, 0.0, 2_096.4],
            "age": [40.0, 8.0, 55.0, 70.0],
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


@pytest.mark.parametrize("year", [2025, 2026, 2034, 2036])
@pytest.mark.parametrize("variable, series", sorted(SERIES.items()))
def test_dataset_extension_uprates_by_the_index(variable, series, year):
    base, later = _extended().datasets[BASE_YEAR], _extended().datasets[year]
    for before, after in zip(base.person[variable], later.person[variable]):
        assert after == pytest.approx(before * _ratio(series, year), rel=1e-9)
    assert _weighted_total(later, variable) / _weighted_total(
        base, variable
    ) == pytest.approx(_ratio(series, year) * _ratio(POPULATION_PATH, year), rel=1e-9)
