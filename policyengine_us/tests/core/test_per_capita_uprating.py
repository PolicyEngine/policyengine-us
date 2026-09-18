"""Dollar inputs uprate by per-capita growth, so weighted totals track the
national totals they follow instead of counting population growth twice."""

from functools import lru_cache

import numpy as np
import pandas as pd
import pytest
from policyengine_core.parameters.operations.get_parameter import get_parameter
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.data.economic_assumptions import (
    MICRODATA_UPRATING_OVERRIDES,
    _resolve_uprating_parameter,
    extend_single_year_dataset,
)
from policyengine_us.reforms.ssa import apply_trustees_2025_economic_assumptions
from policyengine_us.system import system
from policyengine_us.tools.per_capita_uprating import (
    PER_CAPITA_SUFFIX,
    POPULATION_PATH,
    add_per_capita_uprating,
    is_national_total_path,
    per_capita_path,
)

SOI_EMPLOYMENT = "calibration.gov.irs.soi.employment_income"
CBO_AGI = "calibration.gov.cbo.income_by_source.adjusted_gross_income"
CMS_MOOP = "calibration.gov.hhs.cms.moop_per_capita"
CPI_U = "gov.bls.cpi.cpi_u"
YEARS = (2025, 2030, 2035)
BASE_YEAR = 2024


def _value(path, year, parameters=None):
    parameters = system.parameters if parameters is None else parameters
    return get_parameter(parameters, path)(f"{year}-01-01")


def _growth(path, year, parameters=None):
    return _value(path, year, parameters) / _value(path, BASE_YEAR, parameters)


@pytest.mark.parametrize(
    "path, expected",
    [
        (SOI_EMPLOYMENT, True),
        (CBO_AGI, True),
        ("calibration.gov.cbo.unemployment_compensation", True),
        (CMS_MOOP, False),
        (CPI_U, False),
        (POPULATION_PATH, False),
        (per_capita_path(SOI_EMPLOYMENT), False),
        (None, False),
    ],
)
def test_national_total_paths_are_identified(path, expected):
    assert is_national_total_path(path) is expected


def test_no_variable_uprates_by_a_national_total():
    offenders = {
        variable.name: variable.uprating
        for variable in system.variables.values()
        if is_national_total_path(variable.uprating)
    }
    assert offenders == {}


@pytest.mark.parametrize(
    "variable, expected",
    [
        ("employment_income_before_lsr", per_capita_path(SOI_EMPLOYMENT)),
        ("pre_subsidy_rent", per_capita_path(CBO_AGI)),
        ("spm_unit_pre_subsidy_childcare_expenses", per_capita_path(CBO_AGI)),
        ("other_medical_expenses", CMS_MOOP),
        ("child_support_expense", CPI_U),
        ("household_weight", POPULATION_PATH),
    ],
)
def test_variables_point_at_the_expected_series(variable, expected):
    assert system.variables[variable].uprating == expected


def test_every_per_capita_series_is_its_total_over_population():
    paths = {
        variable.uprating
        for variable in system.variables.values()
        if variable.uprating and variable.uprating.endswith(PER_CAPITA_SUFFIX)
    }
    totals = {path[: -len(PER_CAPITA_SUFFIX)] for path in paths} - {
        # CMS publishes this series per capita; it has no total to divide.
        CMS_MOOP[: -len(PER_CAPITA_SUFFIX)]
    }
    assert len(totals) >= 18
    for total in totals:
        for year in (2015, 2017, BASE_YEAR, *YEARS, 2050):
            expected = _value(total, year) / _value(POPULATION_PATH, year)
            assert _value(per_capita_path(total), year) == pytest.approx(
                expected, rel=1e-12
            )


def test_microdata_overrides_resolve_to_per_capita_series():
    for column, path in MICRODATA_UPRATING_OVERRIDES.items():
        resolved = _resolve_uprating_parameter(system.parameters, path)
        assert resolved is not None, column
        if is_national_total_path(path):
            assert resolved.name == per_capita_path(path), column
        else:
            assert resolved.name == path, column


def _tiny_dataset():
    person = pd.DataFrame(
        {
            "person_id": [1, 2, 3, 4],
            "person_household_id": [1, 1, 2, 3],
            "employment_income_before_lsr": [50_000.0, 0.0, 120_000.0, 30_000.0],
            "pre_subsidy_rent": [12_000.0, 0.0, 30_000.0, 9_000.0],
            "other_medical_expenses": [500.0, 250.0, 4_000.0, 0.0],
            "child_support_expense": [0.0, 0.0, 6_000.0, 0.0],
            "age": [40.0, 8.0, 55.0, 70.0],
        }
    )
    household = pd.DataFrame(
        {
            "household_id": [1, 2, 3],
            "household_weight": [1_000.0, 2_500.0, 400.0],
        }
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


def _weighted_total(dataset, column):
    weights = dataset.household.set_index("household_id")["household_weight"]
    person_weights = dataset.person["person_household_id"].map(weights)
    return float((dataset.person[column] * person_weights).sum())


@lru_cache(maxsize=1)
def _extended():
    return extend_single_year_dataset(_tiny_dataset(), end_year=2035, system=system)


@pytest.mark.parametrize("year", YEARS)
def test_extended_dataset_totals_track_national_totals(year):
    base, later = _extended().datasets[BASE_YEAR], _extended().datasets[year]

    def growth(column):
        return _weighted_total(later, column) / _weighted_total(base, column)

    population = _growth(POPULATION_PATH, year)
    assert later.household["household_weight"].sum() / base.household[
        "household_weight"
    ].sum() == pytest.approx(population, rel=1e-9)
    # National totals: the weighted total follows the total itself.
    assert growth("employment_income_before_lsr") == pytest.approx(
        _growth(SOI_EMPLOYMENT, year), rel=1e-9
    )
    assert growth("pre_subsidy_rent") == pytest.approx(_growth(CBO_AGI, year), rel=1e-9)
    # Per-person rates and price indices: amounts follow the series and the
    # weights add population growth.
    assert growth("other_medical_expenses") == pytest.approx(
        _growth(CMS_MOOP, year) * population, rel=1e-9
    )
    assert growth("child_support_expense") == pytest.approx(
        _growth(CPI_U, year) * population, rel=1e-9
    )
    # Inputs without an uprating parameter carry over unchanged.
    assert later.person["age"].tolist() == base.person["age"].tolist()


def test_simulation_uprating_tracks_national_totals():
    simulation = Simulation(
        situation={
            "people": {
                "adult": {
                    "age": {BASE_YEAR: 40},
                    "employment_income_before_lsr": {BASE_YEAR: 50_000},
                }
            },
            "households": {
                "household": {
                    "members": ["adult"],
                    "household_weight": {BASE_YEAR: 1_000},
                }
            },
        }
    )
    for year in YEARS:
        income = simulation.calculate("employment_income_before_lsr", year)[0]
        weight = simulation.calculate("household_weight", year)[0]
        assert income / 50_000 == pytest.approx(
            _growth(per_capita_path(SOI_EMPLOYMENT), year), rel=1e-6
        )
        assert (income * weight) / (50_000 * 1_000) == pytest.approx(
            _growth(SOI_EMPLOYMENT, year), rel=1e-6
        )


class _LargerPopulation(Reform):
    def apply(self):
        def modify(parameters):
            population = get_parameter(parameters, POPULATION_PATH)
            # System init applies a reform twice, so set an absolute value.
            population.update(
                period="year:2030-01-01:1",
                value=_value(POPULATION_PATH, 2030) * 2,
            )
            return parameters

        self.modify_parameters(modify)


def test_reform_to_population_reaches_per_capita_series():
    reformed = CountryTaxBenefitSystem(reform=_LargerPopulation).parameters
    path = per_capita_path(SOI_EMPLOYMENT)
    assert _value(path, 2030, reformed) == pytest.approx(
        _value(path, 2030) / 2, rel=1e-12
    )
    assert _value(path, 2029, reformed) == pytest.approx(_value(path, 2029), rel=1e-12)


def test_rebuilding_is_idempotent():
    rebuilt = CountryTaxBenefitSystem()
    before = {v.name: v.uprating for v in rebuilt.variables.values()}
    value = _value(per_capita_path(CBO_AGI), 2030, rebuilt.parameters)
    add_per_capita_uprating(rebuilt)
    assert {v.name: v.uprating for v in rebuilt.variables.values()} == before
    assert _value(per_capita_path(CBO_AGI), 2030, rebuilt.parameters) == value


class _Trustees2025(Reform):
    def apply(self):
        def modify(parameters):
            apply_trustees_2025_economic_assumptions(parameters)
            return parameters

        self.modify_parameters(modify)


def test_trustees_long_run_incomes_grow_with_average_wages():
    """The Trustees scenario ages each record's income with the average wage
    after the CBO window; population growth belongs to the weights."""
    parameters = CountryTaxBenefitSystem(reform=_Trustees2025).parameters
    path = per_capita_path(SOI_EMPLOYMENT)
    for year in (2040, 2050):
        wage_growth = _value("gov.ssa.nawi", year, parameters) / _value(
            "gov.ssa.nawi", year - 1, parameters
        )
        per_record_growth = _value(path, year, parameters) / _value(
            path, year - 1, parameters
        )
        assert per_record_growth == pytest.approx(wage_growth, rel=1e-9)
