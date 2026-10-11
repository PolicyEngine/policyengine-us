"""Employer plan premium inputs age with CMS's employer-sponsored insurance
(ESI) premium per enrollee, not with wages or out-of-pocket spending.

CMS's National Health Expenditure projections (Table 17, 2025-2034 release)
report ESI spending, ESI enrollment and ESI spending per enrollee for 2013 to
2034. ESI spending is premiums paid by employers and employees (NHEA
methodology paper, p. 28), so spending per enrollee is the premium per covered
person. The parameter holds that row; later years hold its 2033-2034 growth
rate.

Invariants:

1. Transcription: every value equals Table 17's ESI spending over ESI
   enrollment, within the table's rounding.
2. Employer share: CMS projects employer contributions (Table 16) as a flat
   share of ESI spending, so employer contributions per ESI enrollee grow with
   the index. That is why one index serves the employer and employee shares.
3. Bounds and order: the index is positive in every year and strictly
   increasing, as CMS's series is in every year from 2013 to 2034; the
   extension keeps both through 2100.
4. Extension rule: each year after 2034 grows by 13,124 / 12,559.
5. Uprating: a premium entered for one year equals that amount times the
   index ratio in any later year, for both premium inputs, in a household
   simulation and in dataset extension, so uprating is linear in the amount.
6. Weighted totals: in an extended dataset the weighted total grows by the
   index ratio times population growth, because weights follow population.
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
PREMIUM_INPUTS = (
    "employer_sponsored_insurance_premiums",
    "pre_tax_health_insurance_premiums",
)
BASE_YEAR = 2024
FIRST_YEAR, LAST_PROJECTED_YEAR, END_YEAR = 2013, 2034, 2100

# CMS NHE projections tables, Table 17, "Employer-sponsored Insurance" rows
# (https://www.cms.gov/files/zip/nhe-projections-tables.zip, Last-Modified
# 2026-09-03, sha256 264f8226...cd70).
ESI_SPENDING_BILLIONS = dict(
    zip(
        range(2013, 2035),
        (
            *(829.1, 845.4, 880.5, 926.8, 965.7, 1013.1, 1050.3, 1052.7),
            *(1120.9, 1203.9, 1333.5, 1429.1, 1549.8, 1650.5, 1732.9),
            *(1820.4, 1896.9, 1978.0, 2058.6, 2148.4, 2246.7, 2343.1),
        ),
    )
)
ESI_ENROLLMENT_MILLIONS = dict(
    zip(
        range(2013, 2035),
        (
            *(169.2, 169.8, 172.2, 173.1, 175.6, 175.2, 176.4, 174.0),
            *(173.6, 175.1, 175.6, 178.6, 179.9, 179.8, 180.0, 180.4),
            *(180.1, 179.8, 179.5, 179.2, 178.9, 178.5),
        ),
    )
)
# Table 16, employer contributions to private health insurance premiums by
# private business, the federal government and state and local governments.
EMPLOYER_CONTRIBUTIONS_BILLIONS = {
    2024: 753 + 47 + 247,
    2026: 865 + 56 + 288,
    2034: 1_207 + 82 + 429,
}


def _index(year):
    return get_parameter(system.parameters, ESI)(f"{year}-01-01")


def _ratio(year, base_year=BASE_YEAR):
    return _index(year) / _index(base_year)


@pytest.mark.parametrize("year", sorted(ESI_SPENDING_BILLIONS))
def test_index_is_table_17_spending_over_enrollment(year):
    spending = ESI_SPENDING_BILLIONS[year]
    enrollment = ESI_ENROLLMENT_MILLIONS[year]
    # Both components are rounded to one decimal and the published value to
    # the dollar.
    low = 1_000 * (spending - 0.05) / (enrollment + 0.05) - 0.5
    high = 1_000 * (spending + 0.05) / (enrollment - 0.05) + 0.5
    assert low <= _index(year) <= high


@pytest.mark.parametrize("start, end", [(2024, 2034), (2026, 2034)])
def test_employer_contributions_per_enrollee_grow_with_the_index(start, end):
    def per_enrollee(year):
        return EMPLOYER_CONTRIBUTIONS_BILLIONS[year] / ESI_ENROLLMENT_MILLIONS[year]

    years = end - start
    employer_growth = (per_enrollee(end) / per_enrollee(start)) ** (1 / years)
    index_growth = _ratio(end, start) ** (1 / years)
    assert employer_growth == pytest.approx(index_growth, abs=0.001)
    # The employer share of ESI premiums stays within 73.2% to 73.4%.
    for year in (start, end):
        share = EMPLOYER_CONTRIBUTIONS_BILLIONS[year] / ESI_SPENDING_BILLIONS[year]
        assert 0.732 <= share <= 0.734


@given(
    st.integers(FIRST_YEAR, END_YEAR - 1),
    st.integers(1, END_YEAR - FIRST_YEAR),
)
def test_index_is_positive_and_strictly_increasing(year, gap):
    later = min(year + gap, END_YEAR)
    assert 0 < _index(year) < _index(later)


@given(st.integers(LAST_PROJECTED_YEAR + 1, END_YEAR))
def test_extension_holds_the_last_projected_growth_rate(year):
    last_growth = _index(LAST_PROJECTED_YEAR) / _index(LAST_PROJECTED_YEAR - 1)
    assert last_growth == pytest.approx(13_124 / 12_559, rel=1e-12)
    assert _index(year) / _index(year - 1) == pytest.approx(last_growth, rel=1e-12)


@pytest.mark.parametrize("variable", PREMIUM_INPUTS)
def test_premium_inputs_uprate_by_the_esi_index(variable):
    assert system.variables[variable].uprating == ESI


def _simulation(amounts):
    people = {
        f"person_{i}": {
            "age": {BASE_YEAR: 40},
            PREMIUM_INPUTS[0]: {BASE_YEAR: employer},
            PREMIUM_INPUTS[1]: {BASE_YEAR: employee},
        }
        for i, (employer, employee) in enumerate(amounts)
    }
    return Simulation(
        situation={
            "people": people,
            "households": {"household": {"members": list(people)}},
        }
    )


@settings(
    max_examples=10,
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
        min_size=1,
        max_size=8,
    ),
    st.lists(st.integers(BASE_YEAR + 1, END_YEAR), min_size=1, max_size=4),
)
def test_simulation_uprates_premiums_by_the_index_ratio(amounts, years):
    simulation = _simulation(amounts)
    for year in years:
        for column, variable in enumerate(PREMIUM_INPUTS):
            values = simulation.calculate(variable, year)
            for value, base in zip(values, (pair[column] for pair in amounts)):
                assert value == pytest.approx(base * _ratio(year), rel=1e-6, abs=0.01)


@pytest.mark.parametrize("year", [2025, 2030, 2034, 2035, 2036])
def test_simulation_uprates_a_household_premium(year):
    simulation = _simulation([(10_000.0, 2_500.0)])
    employer = simulation.calculate(PREMIUM_INPUTS[0], year)[0]
    employee = simulation.calculate(PREMIUM_INPUTS[1], year)[0]
    assert employer == pytest.approx(10_000 * _ratio(year), rel=1e-6)
    assert employee == pytest.approx(2_500 * _ratio(year), rel=1e-6)


def _tiny_dataset():
    person = pd.DataFrame(
        {
            "person_id": [1, 2, 3, 4],
            "person_household_id": [1, 1, 2, 3],
            "employer_sponsored_insurance_premiums": [14_000.0, 0.0, 6_500.0, 0.0],
            "pre_tax_health_insurance_premiums": [4_200.0, 0.0, 1_100.0, 900.0],
            "age": [40.0, 8.0, 55.0, 62.0],
        }
    )
    household = pd.DataFrame(
        {"household_id": [1, 2, 3], "household_weight": [1_000.0, 2_500.0, 400.0]}
    )
    return USSingleYearDataset(
        person=person,
        household=household,
        tax_unit=pd.DataFrame({"tax_unit_id": [1, 2, 3]}),
        spm_unit=pd.DataFrame({"spm_unit_id": [1, 2, 3]}),
        family=pd.DataFrame({"family_id": [1, 2, 3]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [1, 2, 3, 4]}),
        time_period=BASE_YEAR,
    )


@lru_cache(maxsize=1)
def _extended():
    return extend_single_year_dataset(_tiny_dataset(), end_year=2036, system=system)


def _weighted_total(dataset, column):
    weights = dataset.household.set_index("household_id")["household_weight"]
    person_weights = dataset.person["person_household_id"].map(weights)
    return float((dataset.person[column] * person_weights).sum())


@pytest.mark.parametrize("year", [2025, 2030, 2034, 2036])
@pytest.mark.parametrize("variable", PREMIUM_INPUTS)
def test_dataset_extension_uprates_by_the_index(variable, year):
    base, later = _extended().datasets[BASE_YEAR], _extended().datasets[year]
    for before, after in zip(base.person[variable], later.person[variable]):
        assert after == pytest.approx(before * _ratio(year), rel=1e-9)
    population = get_parameter(system.parameters, POPULATION_PATH)
    population_growth = population(f"{year}-01-01") / population(f"{BASE_YEAR}-01-01")
    assert _weighted_total(later, variable) / _weighted_total(
        base, variable
    ) == pytest.approx(_ratio(year) * population_growth, rel=1e-9)
