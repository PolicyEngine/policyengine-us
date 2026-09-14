"""Synthetic mixed-universe contracts requiring the Python simulation API.

YAML covers the ordinary-housing bridge's scalar arithmetic. These tests inspect
provider calls, missing outputs, independent entity membership, and preservation
of explicitly supplied source data; the YAML runner cannot express those checks.
No native population data, data build, or default dataset is used.
"""

from importlib import import_module
import socket

import h5py
import numpy as np
import pandas as pd
import pytest
import requests
from spm_calculator.errors import SPMInputError
from spm_calculator.policyengine_adapter import PolicyEngineSPMProvider

from policyengine_us import Microsimulation, Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.system import CountryTaxBenefitSystem


YEAR = 2024
STATUS = "spm_unit_spm_universe_status"
REPORTED = "spm_unit_ordinary_housing_subsidy_reported"
ORDINARY_HOUSING = "spm_unit_ordinary_housing_subsidy"
POVERTY_INDICATORS = (
    "spm_unit_is_in_spm_poverty",
    "spm_unit_is_in_deep_spm_poverty",
    "in_poverty",
    "in_deep_poverty",
    "person_in_poverty",
)
MEASUREMENT_AMOUNTS = (
    "spm_unit_reference_spm_threshold",
    "spm_unit_unadjusted_spm_threshold",
    "spm_unit_spm_threshold",
    "spm_unit_spm_threshold_housing_portion",
    "spm_unit_geographic_adjustment",
    "spm_unit_capped_housing_subsidy",
    "spm_unit_benefits",
    "spm_unit_net_income",
    "poverty_line",
    "deep_poverty_line",
    "poverty_gap",
    "deep_poverty_gap",
)


@pytest.fixture(autouse=True)
def no_population_data_reads(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("Mixed SPM tests must not read population data")

    monkeypatch.setattr(requests.sessions.Session, "request", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(pd, "HDFStore", forbidden)
    monkeypatch.setattr(h5py, "File", forbidden)


@pytest.fixture
def mixed_source():
    """One ordinary parent/child unit and one source-marked GQ child unit."""
    groups = ("household", "tax_unit", "spm_unit", "family")
    return USSingleYearDataset(
        person=pd.DataFrame(
            {
                "person_id": [101, 102, 301],
                "age": [40, 8, 12],
                "employment_income": [6_000.0, 0.0, 0.0],
                "is_spm_independent_minor_role": [False, False, False],
                "is_household_head": [True, False, False],
                "is_tax_unit_head": [True, False, True],
                "is_tax_unit_dependent": [False, True, False],
                **{f"person_{entity}_id": [10, 10, 30] for entity in groups},
                "person_marital_unit_id": [101, 102, 301],
            }
        ),
        household=pd.DataFrame(
            {
                "household_id": [10, 30],
                "state_code": ["CA", "CA"],
                # The outside record deliberately lacks SPM geography.
                "county_fips": ["06037", ""],
                "household_weight": [2.0, 5.0],
            }
        ),
        tax_unit=pd.DataFrame({"tax_unit_id": [10, 30]}),
        family=pd.DataFrame({"family_id": [10, 30]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [101, 102, 301]}),
        spm_unit=pd.DataFrame(
            {
                "spm_unit_id": [10, 30],
                STATUS: ["INCLUDED", "OUTSIDE"],
                # Included source valuation must not replace the legacy cap.
                REPORTED: [123.0, 30_000.0],
                "spm_unit_tenure_type": ["RENTER", "RENTER"],
                "is_eligible_for_housing_assistance": [True, True],
                "takes_up_housing_assistance_if_eligible": [True, True],
                "hud_hap": [30_000.0, 30_000.0],
                "hud_ttp": [1_000.0, 1_000.0],
            }
        ),
        time_period=YEAR,
    )


def _only_included(source):
    """A separately built comparison fixture with the identical ordinary unit."""
    return USSingleYearDataset(
        person=source.person.loc[source.person.person_household_id == 10].copy(),
        household=source.household.loc[source.household.household_id == 10].copy(),
        tax_unit=source.tax_unit.loc[source.tax_unit.tax_unit_id == 10].copy(),
        spm_unit=source.spm_unit.loc[source.spm_unit.spm_unit_id == 10].copy(),
        family=source.family.loc[source.family.family_id == 10].copy(),
        marital_unit=source.marital_unit.loc[
            source.marital_unit.marital_unit_id.isin([101, 102])
        ].copy(),
        time_period=YEAR,
    )


def _capture_provider(monkeypatch):
    calls = []
    original = PolicyEngineSPMProvider.calculate_unit

    def capture(self, **kwargs):
        calls.append(kwargs.copy())
        assert kwargs["adults"] >= 1, "Outside child-only unit reached SPM provider"
        assert kwargs.get("county_fips") != "", "Outside geography reached provider"
        return original(self, **kwargs)

    monkeypatch.setattr(PolicyEngineSPMProvider, "calculate_unit", capture)
    return calls


@pytest.mark.parametrize("simulation_type", [Simulation, Microsimulation])
def test_mixed_measurement_retains_included_values_and_missing_outside(
    mixed_source, monkeypatch, simulation_type
):
    calls = _capture_provider(monkeypatch)
    simulation = simulation_type(dataset=mixed_source)
    included = simulation_type(dataset=_only_included(mixed_source))
    for variable in (*MEASUREMENT_AMOUNTS, *POVERTY_INDICATORS):
        actual = simulation.calculate(variable, YEAR, map_to="person")
        expected = included.calculate(variable, YEAR, map_to="person")
        assert np.issubdtype(actual.dtype, np.floating), variable
        np.testing.assert_array_equal(actual[:2], expected, err_msg=variable)
        assert np.isnan(actual[2]), f"{variable} outside must be missing, never false"
        if simulation_type is Microsimulation and variable in POVERTY_INDICATORS:
            # The two included people inherit household weight 2; the outside
            # person's weight 5 must not enter the measurement denominator.
            assert actual.count() == 4
            assert actual.mean() == expected.mean()
    assert calls, "Included units must execute the real canonical provider"
    assert {call["year"] for call in calls} == {YEAR}
    assert {call["county_fips"] for call in calls} == {"06037"}
    np.testing.assert_array_equal(
        simulation.calculate("person_id", YEAR), [101, 102, 301]
    )
    np.testing.assert_array_equal(simulation.calculate("spm_unit_size", YEAR), [2, 1])
    np.testing.assert_array_equal(
        simulation.calculate("spm_unit_count_children", YEAR), [1, 1]
    )


def test_ordinary_bridge_preserves_cap_and_explicit_outside_housing_value(
    mixed_source, monkeypatch
):
    calls = _capture_provider(monkeypatch)
    simulation = Microsimulation(dataset=mixed_source)
    actual_assistance = simulation.calculate("housing_assistance", YEAR)
    ordinary = simulation.calculate(ORDINARY_HOUSING, YEAR)
    capped = simulation.calculate("spm_unit_capped_housing_subsidy", YEAR)
    np.testing.assert_array_equal(actual_assistance, [30_000, 30_000])
    assert 123 < ordinary[0] < 30_000
    assert ordinary[0] == capped[0]
    assert ordinary[1] == 30_000
    assert np.isnan(capped[1])
    assert calls
    assert all(call["adults"] == 1 and call["children"] == 1 for call in calls)


def test_excluded_spm_measurement_does_not_require_an_ordinary_housing_valuation(
    mixed_source, monkeypatch
):
    source = mixed_source.copy()
    source.spm_unit.drop(columns=[REPORTED], inplace=True)
    _capture_provider(monkeypatch)
    simulation = Microsimulation(dataset=source)
    poverty = simulation.calculate("spm_unit_is_in_spm_poverty", YEAR, map_to="person")
    assert poverty.count() == 4
    assert np.isnan(poverty.iloc[2])


@pytest.mark.parametrize(
    "variable",
    [
        "household_benefits",
        "household_net_income",
        "cbo_household_means_tested_transfers",
        "ca_cpuc_countable_income",
    ],
)
def test_ordinary_consumers_keep_mixed_population_and_reported_housing_component(
    mixed_source, monkeypatch, variable
):
    _capture_provider(monkeypatch)
    if variable == "cbo_household_means_tested_transfers":
        # Dataset Medicaid allocates each state's spending over that dataset's
        # enrollees. This tiny fixture therefore receives billions per person,
        # as it does on unchanged 2.1.0, losing housing-dollar float32 precision.
        # Fix health transfers only for this isolated housing-component check;
        # it makes no claim about absolute CBO or Medicaid benefit amounts.
        mixed_source.person["medicaid"] = [0.0, 0.0, 0.0]
        mixed_source.person["chip"] = [0.0, 0.0, 0.0]
    source_without_value = mixed_source.copy()
    source_without_value.spm_unit[REPORTED] = [123.0, 0.0]
    simulation = Microsimulation(dataset=mixed_source)
    comparison = Microsimulation(dataset=source_without_value)
    actual = simulation.calculate(variable, YEAR)
    baseline = comparison.calculate(variable, YEAR)
    assert len(actual) == 2, (
        "Ordinary resource consumers must retain outside households"
    )
    assert np.isfinite(actual).all(), variable
    assert actual[0] == baseline[0], variable
    # Only the source valuation changes; actual HUD assistance remains fixed.
    assert actual[1] - baseline[1] == pytest.approx(30_000, abs=0.01), variable
    np.testing.assert_array_equal(
        simulation.calculate("housing_assistance", YEAR),
        comparison.calculate("housing_assistance", YEAR),
    )


@pytest.mark.parametrize("reported", [None, -1.0, float("inf"), 30_001.0])
def test_positive_outside_housing_requires_a_valid_explicit_value(
    mixed_source, reported
):
    source = mixed_source.copy()
    if reported is None:
        source.spm_unit.drop(columns=[REPORTED], inplace=True)
    else:
        source.spm_unit[REPORTED] = [123.0, reported]
    with pytest.raises(SPMInputError) as error:
        Microsimulation(dataset=source).calculate(ORDINARY_HOUSING, YEAR)
    assert error.value.code == "SPM_ORDINARY_HOUSING_VALUE_REQUIRED"


@pytest.mark.parametrize("assistance", [-1.0, float("inf")])
def test_invalid_actual_housing_assistance_is_not_treated_as_known_zero(
    mixed_source, assistance
):
    source = mixed_source.copy()
    source.spm_unit["hud_hap"] = [30_000.0, assistance]
    with pytest.raises(SPMInputError) as error:
        Microsimulation(dataset=source).calculate(ORDINARY_HOUSING, YEAR)
    assert error.value.code == "SPM_HOUSING_ASSISTANCE_INVALID"


@pytest.mark.parametrize("variable", [REPORTED, "hud_hap"])
def test_explicit_source_nan_is_rejected_before_ordinary_calculation(
    mixed_source, variable
):
    source = mixed_source.copy()
    source.spm_unit[variable] = [30_000.0, np.nan]
    # Core's input holder rejects NaN before the country formula can run.
    with pytest.raises(ValueError, match="input contains NaN values"):
        Microsimulation(dataset=source)


def test_calculated_nan_assistance_fails_typed_validation(mixed_source, monkeypatch):
    simulation = Microsimulation(dataset=mixed_source)
    original_calculate = simulation.calculate

    def calculate(variable_name, *args, **kwargs):
        if variable_name == "housing_assistance":
            return np.array([30_000.0, np.nan])
        return original_calculate(variable_name, *args, **kwargs)

    # A formula can yield NaN after Core's source-input checks have passed.
    monkeypatch.setattr(simulation, "calculate", calculate)
    with pytest.raises(SPMInputError) as error:
        simulation.calculate(ORDINARY_HOUSING, YEAR)
    assert error.value.code == "SPM_HOUSING_ASSISTANCE_INVALID"


@pytest.mark.parametrize("has_target_year_report", [False, True])
def test_outside_housing_report_must_be_explicit_for_calculation_year(
    mixed_source, has_target_year_report
):
    simulation = Microsimulation(dataset=mixed_source)
    target_year = YEAR + 1
    simulation.set_input(STATUS, target_year, ["OUTSIDE", "OUTSIDE"])
    simulation.set_input("hud_hap", target_year, [30_000.0, 30_000.0])
    simulation.set_input("hud_ttp", target_year, [1_000.0, 1_000.0])
    simulation.set_input(
        "is_eligible_for_housing_assistance", target_year, [True, True]
    )
    simulation.set_input(
        "takes_up_housing_assistance_if_eligible", target_year, [True, True]
    )
    if has_target_year_report:
        simulation.set_input(REPORTED, target_year, [20_000.0, 25_000.0])
        np.testing.assert_array_equal(
            simulation.calculate(ORDINARY_HOUSING, target_year), [20_000, 25_000]
        )
    else:
        with pytest.raises(SPMInputError) as error:
            simulation.calculate(ORDINARY_HOUSING, target_year)
        assert error.value.code == "SPM_ORDINARY_HOUSING_VALUE_REQUIRED"


@pytest.mark.parametrize("source_table", ["spm_unit", "household"])
def test_source_universe_is_not_inferred_for_generated_future_year(
    mixed_source, source_table
):
    source = mixed_source.copy()
    if source_table == "household":
        # The accepted dataset loader flattens entity tables, so a declaration
        # stored on this one-SPM-unit-per-household table is also supplied.
        for variable in (STATUS, REPORTED):
            source.household[variable] = source.spm_unit.pop(variable)
    original_tables = [frame.copy(deep=True) for frame in source.tables]
    simulation = Microsimulation(dataset=source)
    assert list(simulation.calculate(STATUS, YEAR)) == ["INCLUDED", "OUTSIDE"]
    np.testing.assert_array_equal(simulation.calculate(REPORTED, YEAR), [123, 30_000])
    future_status = simulation.calculate(STATUS, YEAR + 1)
    assert list(future_status) == ["UNRESOLVED", "UNRESOLVED"]
    np.testing.assert_array_equal(simulation.calculate(REPORTED, YEAR + 1), [-1, -1])
    with pytest.raises(SPMInputError):
        simulation.calculate("spm_unit_spm_threshold", YEAR + 1)
    for original, current in zip(original_tables, source.tables):
        pd.testing.assert_frame_equal(original, current)


@pytest.mark.parametrize("earnings,expected_poor", [(0.0, 1.0), (100_000.0, 0.0)])
def test_monthly_poverty_status_preserves_annual_boolean_values_and_missingness(
    mixed_source, earnings, expected_poor
):
    source = mixed_source.copy()
    # A single included adult with zero or high earnings makes both ordinary
    # and deep-poverty outcomes unambiguous, alongside the outside child.
    source.person = source.person.loc[source.person.person_id != 102].copy()
    source.marital_unit = source.marital_unit.loc[
        source.marital_unit.marital_unit_id != 102
    ].copy()
    source.person["employment_income"] = [earnings, 0.0]
    source.spm_unit["hud_hap"] = [0.0, 30_000.0]
    simulation = Microsimulation(dataset=source)
    for variable in POVERTY_INDICATORS:
        annual = simulation.calculate(variable, YEAR, map_to="person")
        monthly = simulation.calculate(variable, f"{YEAR}-01", map_to="person")
        assert annual.iloc[0] == expected_poor, variable
        np.testing.assert_array_equal(monthly, annual, err_msg=variable)
        assert np.isnan(monthly.iloc[1]), variable
        assert monthly.count() == annual.count() == 2
        assert monthly.mean() == annual.mean() == expected_poor


def test_known_zero_outside_assistance_needs_no_reported_value_or_provider(
    mixed_source, monkeypatch
):
    source = mixed_source.copy()
    source.spm_unit[STATUS] = ["OUTSIDE", "OUTSIDE"]
    source.spm_unit["hud_hap"] = [0.0, 0.0]
    source.spm_unit.drop(columns=[REPORTED], inplace=True)

    def forbidden(*args, **kwargs):
        raise AssertionError("Known-zero outside assistance must not call SPM")

    monkeypatch.setattr(PolicyEngineSPMProvider, "calculate_unit", forbidden)
    simulation = Microsimulation(dataset=source)
    np.testing.assert_array_equal(simulation.calculate(ORDINARY_HOUSING, YEAR), [0, 0])


def test_all_outside_measurements_have_no_provider_calls_or_poverty_denominator(
    mixed_source, monkeypatch
):
    source = mixed_source.copy()
    source.spm_unit[STATUS] = ["OUTSIDE", "OUTSIDE"]

    def forbidden(*args, **kwargs):
        raise AssertionError("An all-outside population must not execute SPM")

    monkeypatch.setattr(PolicyEngineSPMProvider, "calculate_unit", forbidden)
    simulation = Microsimulation(dataset=source)
    for variable in ("spm_unit_spm_threshold", *POVERTY_INDICATORS):
        result = simulation.calculate(variable, YEAR, map_to="person")
        assert np.isnan(result).all(), variable
        assert result.count() == 0, variable
        assert np.isnan(result.mean()), variable


@pytest.mark.parametrize(
    "variable", ["household_net_income", "spm_unit_spm_threshold", *POVERTY_INDICATORS]
)
def test_unresolved_measurement_status_fails_closed(
    mixed_source, variable, monkeypatch
):
    source = mixed_source.copy()
    # Make both units calculable so composition/geography errors cannot mask
    # a missing check for the unresolved source classification.
    source.person["age"] = [40, 8, 40]
    source.household["county_fips"] = ["06037", "36061"]
    source.spm_unit[STATUS] = ["INCLUDED", "UNRESOLVED"]

    def forbidden(*args, **kwargs):
        raise AssertionError("Unresolved measurement scope must fail before SPM")

    monkeypatch.setattr(PolicyEngineSPMProvider, "calculate_unit", forbidden)
    with pytest.raises(SPMInputError) as error:
        Microsimulation(dataset=source).calculate(variable, YEAR)
    assert error.value.code == "SPM_UNIVERSE_REQUIRED"


def test_dataset_without_source_universe_defaults_to_unresolved(mixed_source):
    source = mixed_source.copy()
    source.person["age"] = [40, 8, 40]
    source.household["county_fips"] = ["06037", "36061"]
    source.spm_unit.drop(columns=[STATUS], inplace=True)
    simulation = Microsimulation(dataset=source)
    with pytest.raises(SPMInputError) as error:
        simulation.calculate("spm_unit_spm_threshold", YEAR)
    assert error.value.code == "SPM_UNIVERSE_REQUIRED"


def test_ordinary_household_situation_keeps_included_default():
    simulation = Simulation(
        situation={
            "people": {"person1": {"age": {YEAR: 40}}},
            "households": {
                "household1": {"members": ["person1"], "county_fips": {YEAR: "06037"}}
            },
        }
    )
    assert simulation.calculate("spm_unit_spm_threshold", YEAR)[0] > 0


@pytest.mark.parametrize("variable", [*POVERTY_INDICATORS, ORDINARY_HOUSING])
@pytest.mark.parametrize("ingress", ["dataset", "set_input"])
def test_computed_poverty_and_housing_outputs_cannot_be_supplied_as_inputs(
    mixed_source, variable, ingress
):
    from policyengine_us.system import system

    entity = system.variables[variable].entity.key
    source = mixed_source.copy()
    frame = getattr(source, entity)
    if ingress == "dataset":
        frame[variable] = 1.0
        with pytest.raises(ValueError, match="formula-owned"):
            Microsimulation(dataset=source)
    else:
        simulation = Microsimulation(dataset=source)
        with pytest.raises(ValueError, match="formula-owned"):
            simulation.set_input(variable, YEAR, np.ones(len(frame)))


def test_mixed_calculations_preserve_source_tables_and_membership(mixed_source):
    before = [frame.copy(deep=True) for frame in mixed_source.tables]
    simulation = Microsimulation(dataset=mixed_source)
    simulation.calculate("household_net_income", YEAR)
    simulation.calculate("spm_unit_is_in_spm_poverty", YEAR)
    for original, current in zip(before, mixed_source.tables):
        pd.testing.assert_frame_equal(original, current)
    for entity in ("household", "tax_unit", "spm_unit", "family", "marital_unit"):
        np.testing.assert_array_equal(
            simulation.calculate(f"person_{entity}_id", YEAR),
            mixed_source.person[f"person_{entity}_id"],
        )


@pytest.mark.parametrize(
    "module_name,factory_name",
    [
        pytest.param(
            "congress.tlaib.boost.boost_middle_class_tax_credit",
            "create_boost_middle_class_tax_credit",
            id="boost",
        ),
        pytest.param(
            "congress.tlaib.end_child_poverty_act",
            "create_end_child_poverty_act",
            id="ecpa",
        ),
        pytest.param(
            "congress.tlaib.economic_dignity_for_all_agenda.edaa_end_child_poverty_act",
            "create_ecpa_only",
            id="edaa",
        ),
        pytest.param("states.tx.rebate.tx_rebate", "create_tx_rebate", id="tx-rebate"),
    ],
)
@pytest.mark.parametrize("abolish_housing", [False, True])
def test_contributed_benefit_overrides_preserve_universe_separation(
    mixed_source, monkeypatch, module_name, factory_name, abolish_housing
):
    _capture_provider(monkeypatch)
    factory = getattr(
        import_module(f"policyengine_us.reforms.{module_name}"), factory_name
    )
    reform = (
        factory(),
        {"gov.hud.abolition": {f"{YEAR}-01-01.{YEAR}-12-31": abolish_housing}},
    )
    system = CountryTaxBenefitSystem(reform=reform)

    def simulate(source):
        return Microsimulation(
            dataset=source,
            tax_benefit_system=system,
        )

    simulation = simulate(mixed_source)
    standalone = simulate(_only_included(mixed_source))
    measured = simulation.calculate("spm_unit_benefits", YEAR)
    assert measured[0] == standalone.calculate("spm_unit_benefits", YEAR)[0]
    # HUD abolition removes the capped housing term, so an explicit mask must
    # still exclude outside resources even without a NaN from that term.
    assert np.isnan(measured[1])
    ordinary = simulation.calculate("household_benefits", YEAR)
    assert len(ordinary) == 2
    assert np.isfinite(ordinary).all()
    source_without_value = mixed_source.copy()
    source_without_value.spm_unit[REPORTED] = [123.0, 0.0]
    comparison = simulate(source_without_value).calculate("household_benefits", YEAR)
    assert ordinary[0] == comparison[0]
    expected_component = 0 if abolish_housing else 30_000
    assert ordinary[1] - comparison[1] == pytest.approx(expected_component, abs=0.01)
