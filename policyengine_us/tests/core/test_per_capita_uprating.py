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
from policyengine_us.tests.microsimulation.data.fixtures.test_extend_single_year_dataset import (  # noqa: E501
    MockSystem,
    MockVariable,
    build_mock_parameters,
)
from policyengine_us.tools.per_capita_uprating import (
    DERIVED_FROM,
    PER_CAPITA_SUFFIX,
    POPULATION_PATH,
    _add_per_capita_parameter,
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
        # A state total and a head count: national population is the wrong
        # denominator, so these are not treated as national totals.
        ("calibration.gov.aca.spending.state.AL", False),
        ("calibration.gov.aca.enrollment.state.AK", False),
        ("gov.ssa.nawi", False),
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
        ("charitable_cash_donations", per_capita_path(CBO_AGI)),
        ("miscellaneous_income", per_capita_path(CBO_AGI)),
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
            "charitable_cash_donations": [1_200.0, 0.0, 30_000.0, 900.0],
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
    assert growth("charitable_cash_donations") == pytest.approx(
        _growth(CBO_AGI, year), rel=1e-9
    )
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


class _Trustees2025(Reform):
    def apply(self):
        def modify(parameters):
            apply_trustees_2025_economic_assumptions(parameters)
            return parameters

        self.modify_parameters(modify)


@lru_cache(maxsize=1)
def _trustees_parameters():
    return CountryTaxBenefitSystem(reform=_Trustees2025).parameters


def test_trustees_long_run_incomes_grow_with_average_wages():
    """The Trustees scenario ages each record's income with the average wage
    after the CBO window; population growth belongs to the weights."""
    parameters = _trustees_parameters()
    path = per_capita_path(SOI_EMPLOYMENT)
    for year in (2040, 2050):
        wage_growth = _value("gov.ssa.nawi", year, parameters) / _value(
            "gov.ssa.nawi", year - 1, parameters
        )
        per_record_growth = _value(path, year, parameters) / _value(
            path, year - 1, parameters
        )
        assert per_record_growth == pytest.approx(wage_growth, rel=1e-9)


def test_trustees_long_run_holds_after_the_population_series_ends():
    """Population is flat after 2055, so totals and per-record incomes both
    grow with the average wage alone."""
    parameters = _trustees_parameters()
    path = per_capita_path(SOI_EMPLOYMENT)
    assert _value(POPULATION_PATH, 2060, parameters) == _value(
        POPULATION_PATH, 2056, parameters
    )
    wage_growth = _value("gov.ssa.nawi", 2060, parameters) / _value(
        "gov.ssa.nawi", 2059, parameters
    )
    for series in (path, SOI_EMPLOYMENT):
        growth = _value(series, 2060, parameters) / _value(series, 2059, parameters)
        assert growth == pytest.approx(wage_growth, rel=1e-9)
    assert _value(path, 2060, parameters) == pytest.approx(
        _value(SOI_EMPLOYMENT, 2060, parameters)
        / _value(POPULATION_PATH, 2060, parameters),
        rel=1e-12,
    )


def test_smi_threshold_keeps_pace_with_default_incomes():
    """HHS state median income is projected from 2027; it must grow like the
    incomes tested against it, or eligibility drifts with population."""
    for year in (2028, 2030, 2035, 2040):
        threshold = _value("gov.hhs.smi.amount.CA", year) / _value(
            "gov.hhs.smi.amount.CA", 2027
        )
        income = _value(per_capita_path(CBO_AGI), year) / _value(
            per_capita_path(CBO_AGI), 2027
        )
        assert threshold == pytest.approx(income, rel=1e-9)


def test_derived_series_are_reachable_through_at_instant_views():
    node = system.parameters("2030-01-01").calibration.gov.irs.soi
    assert node.employment_income_per_capita == pytest.approx(
        _value(per_capita_path(SOI_EMPLOYMENT), 2030)
    )


def test_derived_series_are_marked_and_cms_series_is_untouched():
    derived = get_parameter(system.parameters, per_capita_path(SOI_EMPLOYMENT))
    assert derived.metadata[DERIVED_FROM] == SOI_EMPLOYMENT
    cms = get_parameter(system.parameters, CMS_MOOP)
    assert DERIVED_FROM not in cms.metadata
    assert cms.file_path is not None


def test_rebuilds_reforms_and_stale_edits_after_init():
    fresh = CountryTaxBenefitSystem()
    path = per_capita_path(SOI_EMPLOYMENT)
    before = _value(path, 2030, fresh.parameters)

    # Rebuilding is a no-op.
    uprating = {v.name: v.uprating for v in fresh.variables.values()}
    add_per_capita_uprating(fresh)
    assert {v.name: v.uprating for v in fresh.variables.values()} == uprating
    assert _value(path, 2030, fresh.parameters) == before

    # A reform applied after init, as core's Simulation does, refreshes it.
    fresh.apply_reform_set(_LargerPopulation)
    assert _value(path, 2030, fresh.parameters) == pytest.approx(before / 2, rel=1e-12)

    # A parameter edited behind the system's back leaves the series stale;
    # dataset extension refuses to use it.
    total = get_parameter(fresh.parameters, SOI_EMPLOYMENT)
    total.update(period="year:2030-01-01:1", value=total("2030-01-01") * 3)
    with pytest.raises(ValueError, match="out of date"):
        extend_single_year_dataset(_tiny_dataset(), end_year=2030, system=fresh)
    add_per_capita_uprating(fresh)
    extended = extend_single_year_dataset(_tiny_dataset(), end_year=2030, system=fresh)
    assert 2030 in extended.datasets


def test_dataset_extension_reads_the_per_capita_sibling():
    total = {"2024-01-01": 100.0, "2025-01-01": 110.0}
    sibling = {"2024-01-01": 50.0, "2025-01-01": 52.0}
    mock = MockSystem(
        variables={
            "employment_income": MockVariable("employment_income", SOI_EMPLOYMENT)
        },
        parameters=build_mock_parameters(
            {SOI_EMPLOYMENT: total, per_capita_path(SOI_EMPLOYMENT): sibling}
        ),
    )
    dataset = USSingleYearDataset(
        person=pd.DataFrame({"person_id": [1], "employment_income": [1_000.0]}),
        household=pd.DataFrame({"household_id": [1]}),
        tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
        spm_unit=pd.DataFrame({"spm_unit_id": [1]}),
        family=pd.DataFrame({"family_id": [1]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [1]}),
        time_period=BASE_YEAR,
    )
    extended = extend_single_year_dataset(dataset, end_year=2025, system=mock)
    assert extended.datasets[2025].person["employment_income"][0] == pytest.approx(
        1_000.0 * 52.0 / 50.0
    )


def test_missing_per_capita_sibling_raises():
    parameters = build_mock_parameters(
        {SOI_EMPLOYMENT: {"2024-01-01": 100.0}}, per_capita_siblings=False
    )
    with pytest.raises(ValueError, match="national total"):
        _resolve_uprating_parameter(parameters, SOI_EMPLOYMENT)


class _StubVariable:
    def __init__(self, uprating):
        self.uprating = uprating


class _StubSystem:
    def __init__(self, uprating):
        self.variables = {"stub": _StubVariable(uprating)}
        self.parameters = None


def test_unclassified_calibration_path_is_rejected():
    with pytest.raises(ValueError, match="national-total family"):
        add_per_capita_uprating(_StubSystem("calibration.gov.aca.spending.state.AL"))


def test_existing_per_capita_series_is_never_overwritten():
    """A series someone wrote by hand that happens to share the derived name
    must stop the build, not be replaced."""
    from policyengine_core.parameters import ParameterNode

    values = {"values": {"2024-01-01": 10.0}}
    tree = ParameterNode(
        "",
        data={
            "calibration": {
                "gov": {
                    "cbo": {"spending": values, "spending_per_capita": values},
                    "census": {"populations": {"total": values}},
                }
            }
        },
    )
    with pytest.raises(ValueError, match="already exists"):
        _add_per_capita_parameter(tree, "calibration.gov.cbo.spending")
