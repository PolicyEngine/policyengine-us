"""Synthetic mixed-universe contracts requiring the Python simulation API.

These tests inspect
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
from policyengine_core.reforms import Reform
from policyengine_core.variables import Variable

from policyengine_us.data.dataset_schema import USMultiYearDataset, USSingleYearDataset
from policyengine_us.spm import REJECTED_DATASET_INPUTS
from policyengine_us.system import CountryTaxBenefitSystem, system


YEAR = 2024
STATUS = "spm_unit_spm_universe_status"
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
    "spm_unit_oecd_equiv_net_income",
)
DISTRIBUTION_OUTPUTS = ("spm_unit_oecd_equiv_net_income", "spm_unit_income_decile")
ALL_MEASUREMENTS = (*MEASUREMENT_AMOUNTS, *POVERTY_INDICATORS, "spm_unit_income_decile")
ORDINARY_OUTCOMES = (
    "housing_assistance",
    "spm_unit_allocated_housing_subsidy",
    "spm_unit_allocated_tenant_payment",
    "household_benefits",
    "household_net_income",
    "cbo_household_means_tested_transfers",
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


@pytest.mark.parametrize("source_table", ["spm_unit", "household"])
def test_source_universe_is_not_inferred_for_generated_future_year(
    mixed_source, source_table
):
    source = mixed_source.copy()
    if source_table == "household":
        # The accepted dataset loader flattens entity tables, so a declaration
        # stored on this one-SPM-unit-per-household table is also supplied.
        source.household[STATUS] = source.spm_unit.pop(STATUS)
    original_tables = [frame.copy(deep=True) for frame in source.tables]
    simulation = Microsimulation(dataset=source)
    assert list(simulation.calculate(STATUS, YEAR)) == ["INCLUDED", "OUTSIDE"]
    future_status = simulation.calculate(STATUS, YEAR + 1)
    assert list(future_status) == ["UNRESOLVED", "UNRESOLVED"]
    with pytest.raises(SPMInputError):
        simulation.calculate("spm_unit_spm_threshold", YEAR + 1)
    for original, current in zip(original_tables, source.tables):
        pd.testing.assert_frame_equal(original, current)


@pytest.mark.parametrize("earnings,expected_poor", [(0.0, 1.0), (100_000.0, 0.0)])
@pytest.mark.parametrize("month", ["01", "07"])
def test_monthly_poverty_status_preserves_annual_boolean_values_and_missingness(
    mixed_source, earnings, expected_poor, month
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
        monthly = simulation.calculate(variable, f"{YEAR}-{month}", map_to="person")
        assert annual.iloc[0] == expected_poor, variable
        np.testing.assert_array_equal(monthly, annual, err_msg=variable)
        assert np.isnan(monthly.iloc[1]), variable
        assert monthly.count() == annual.count() == 2
        assert monthly.mean() == annual.mean() == expected_poor


def test_all_outside_measurements_have_no_provider_calls_or_poverty_denominator(
    mixed_source, monkeypatch
):
    source = mixed_source.copy()
    source.spm_unit[STATUS] = ["OUTSIDE", "OUTSIDE"]

    def forbidden(*args, **kwargs):
        raise AssertionError("An all-outside population must not execute SPM")

    monkeypatch.setattr(PolicyEngineSPMProvider, "calculate_unit", forbidden)
    simulation = Microsimulation(dataset=source)
    for variable in ALL_MEASUREMENTS:
        result = simulation.calculate(variable, YEAR, map_to="person")
        assert np.isnan(result).all(), variable
        assert result.count() == 0, variable
        assert np.isnan(result.mean()), variable


@pytest.mark.parametrize("variable", ALL_MEASUREMENTS)
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
    source_without_award = mixed_source.copy()
    source_without_award.spm_unit["hud_hap"] = [30_000.0, 0.0]
    comparison = simulate(source_without_award).calculate("household_benefits", YEAR)
    assert ordinary[0] == comparison[0]
    expected_component = 0 if abolish_housing else 30_000
    assert ordinary[1] - comparison[1] == pytest.approx(expected_component, abs=0.01)


@pytest.mark.parametrize("status", ["INCLUDED", "OUTSIDE", "UNRESOLVED", None])
@pytest.mark.parametrize("geography_kind", ["county", "national"])
def test_ordinary_actual_benefits_do_not_require_scope_or_spm_geography(
    mixed_source, monkeypatch, status, geography_kind
):
    source = mixed_source.copy()
    source.household["county_fips"] = ["", ""]
    if status is None:
        source.spm_unit.drop(columns=[STATUS], inplace=True)
    else:
        source.spm_unit[STATUS] = status

    def forbidden(*args, **kwargs):
        raise AssertionError("Ordinary income must not execute SPM measurement")

    monkeypatch.setattr(PolicyEngineSPMProvider, "calculate_unit", forbidden)
    simulation = Microsimulation(dataset=source, spm={"geography_kind": geography_kind})
    # Ordinary benefits may depend on county. Hold that input fixed while
    # varying only the SPM scope declaration and provider selection.
    reference_source = mixed_source.copy()
    reference_source.household["county_fips"] = ["", ""]
    reference_source.spm_unit[STATUS] = "INCLUDED"
    reference = Microsimulation(dataset=reference_source)
    for name in (
        "housing_assistance",
        "household_benefits",
        "household_net_income",
        "cbo_household_means_tested_transfers",
        "ca_cpuc_countable_income",
    ):
        actual = simulation.calculate(name, YEAR)
        assert np.isfinite(actual).all(), name
        np.testing.assert_array_equal(
            actual, reference.calculate(name, YEAR), err_msg=name
        )
    np.testing.assert_array_equal(
        simulation.calculate("housing_assistance", YEAR), [30_000, 30_000]
    )
    assert simulation.spm_provenance()["years"] == {}


@pytest.mark.parametrize("route", ["no_assistance", "hud_abolition"])
@pytest.mark.parametrize(
    "variable",
    [
        "spm_unit_capped_housing_subsidy",
        "spm_unit_benefits",
        "spm_unit_net_income",
        *DISTRIBUTION_OUTPUTS,
        *POVERTY_INDICATORS,
    ],
)
def test_unresolved_scope_precedes_resource_early_returns(
    mixed_source, monkeypatch, variable, route
):
    source = mixed_source.copy()
    source.spm_unit[STATUS] = ["INCLUDED", "UNRESOLVED"]
    source.person["age"] = [40, 8, 40]
    source.household["county_fips"] = ["06037", "36061"]
    if route == "no_assistance":
        source.spm_unit["hud_hap"] = 0.0
        reform = None
    else:
        reform = {"gov.hud.abolition": {f"{YEAR}-01-01.{YEAR}-12-31": True}}

    def forbidden(*args, **kwargs):
        raise AssertionError("Unresolved scope must fail before provider execution")

    monkeypatch.setattr(PolicyEngineSPMProvider, "calculate_unit", forbidden)
    simulation = Microsimulation(dataset=source, reform=reform)
    assert np.isfinite(simulation.calculate("household_net_income", YEAR)).all()
    with pytest.raises(SPMInputError) as error:
        simulation.calculate(variable, YEAR)
    assert error.value.code == "SPM_UNIVERSE_REQUIRED"


@pytest.mark.parametrize("variable", sorted(REJECTED_DATASET_INPUTS))
@pytest.mark.parametrize("ingress", ["dataset", "set_input"])
def test_computed_spm_outputs_cannot_be_supplied_as_inputs(
    mixed_source, variable, ingress
):
    source = mixed_source.copy()
    frame = getattr(source, system.variables[variable].entity.key)
    if ingress == "dataset":
        frame[variable] = 1.0
        with pytest.raises(ValueError, match="formula-owned SPM output"):
            Microsimulation(dataset=source)
    else:
        simulation = Microsimulation(dataset=source)
        with pytest.raises(ValueError, match="formula-owned SPM output"):
            simulation.set_input(variable, YEAR, np.ones(len(frame)))


def test_explicit_multi_year_source_status_is_preserved_without_carry(mixed_source):
    first = mixed_source.copy()
    second = mixed_source.copy()
    second.time_period = str(YEAR + 1)
    second.spm_unit[STATUS] = ["OUTSIDE", "INCLUDED"]
    # Make the newly included unit valid independently of its former status.
    second.person["age"] = [40, 8, 40]
    second.household["county_fips"] = ["06037", "36061"]
    source = USMultiYearDataset(datasets=[first, second])
    originals = {
        year: [table.copy(deep=True) for table in dataset.tables]
        for year, dataset in source.datasets.items()
    }
    simulation = Microsimulation(dataset=source)
    for year, statuses, included_index in (
        (YEAR, ["INCLUDED", "OUTSIDE"], 0),
        (YEAR + 1, ["OUTSIDE", "INCLUDED"], 1),
    ):
        assert list(simulation.calculate(STATUS, year)) == statuses
        threshold = simulation.calculate("spm_unit_spm_threshold", year)
        assert threshold[included_index] > 0
        assert np.isnan(threshold[1 - included_index])
    assert list(simulation.calculate(STATUS, YEAR + 2)) == ["UNRESOLVED"] * 2
    with pytest.raises(SPMInputError) as error:
        simulation.calculate("spm_unit_spm_threshold", YEAR + 2)
    assert error.value.code == "SPM_UNIVERSE_REQUIRED"
    # Revisiting a stored year must not reuse a later year's scope.
    assert list(simulation.calculate(STATUS, YEAR)) == ["INCLUDED", "OUTSIDE"]
    for year, dataset in source.datasets.items():
        for before, after in zip(originals[year], dataset.tables):
            pd.testing.assert_frame_equal(before, after)


@pytest.mark.parametrize("recipient", ["included", "outside"])
def test_shared_household_allocation_retains_outside_members(recipient, monkeypatch):
    calls = _capture_provider(monkeypatch)
    situation = {
        "people": {
            "adult": {"age": {YEAR: 40}},
            "child1": {"age": {YEAR: 12}},
            "child2": {"age": {YEAR: 10}},
        },
        "households": {
            "home": {
                "members": ["adult", "child1", "child2"],
                "county_fips": {YEAR: "06037"},
            }
        },
        "spm_units": {
            "included": {"members": ["adult"], STATUS: {YEAR: "INCLUDED"}},
            "outside": {
                "members": ["child1", "child2"],
                STATUS: {YEAR: "OUTSIDE"},
            },
        },
    }
    for name, unit in situation["spm_units"].items():
        unit["housing_assistance"] = {YEAR: 9_000 if name == recipient else 0}
        unit["hud_ttp"] = {YEAR: 0}
        unit["spm_unit_tenure_type"] = {YEAR: "RENTER"}
    simulation = Simulation(situation=situation)
    expected_awards = [9_000, 0] if recipient == "included" else [0, 9_000]
    np.testing.assert_array_equal(
        simulation.calculate("housing_assistance", YEAR), expected_awards
    )
    np.testing.assert_array_equal(
        simulation.calculate("spm_unit_allocated_housing_subsidy", YEAR), [3_000, 6_000]
    )
    np.testing.assert_array_equal(simulation.calculate("spm_unit_size", YEAR), [1, 2])
    cap = simulation.calculate("spm_unit_capped_housing_subsidy", YEAR)
    housing_portion = simulation.calculate(
        "spm_unit_spm_threshold_housing_portion", YEAR
    )
    assert cap[0] == min(3_000, housing_portion[0])
    assert np.isnan(cap[1])
    assert calls and all(call["adults"] >= 1 for call in calls)
    # Scope masks measurement after member-share allocation; it does not award
    # all of the household's assistance to its one included person.
    np.testing.assert_array_equal(
        simulation.calculate("spm_unit_allocated_housing_subsidy", YEAR), [3_000, 6_000]
    )


def _rank_source(include_outside=True):
    """Unequal included weights and a dominant, very rich outside record."""
    count = 4 if include_outside else 3
    ids = list(range(1, count + 1))
    groups = ("household", "tax_unit", "spm_unit", "family", "marital_unit")
    tables = {entity: pd.DataFrame({f"{entity}_id": ids}) for entity in groups}
    tables["household"]["household_weight"] = [1.0, 2.0, 4.0, 1_000_000.0][:count]
    tables["household"]["county_fips"] = ["06037"] * count
    tables["spm_unit"][STATUS] = ["INCLUDED", "INCLUDED", "INCLUDED", "OUTSIDE"][:count]
    return USSingleYearDataset(
        person=pd.DataFrame(
            {
                "person_id": ids,
                "age": [40] * count,
                "employment_income": [1_000, 10_000, 100_000, 100_000_000][:count],
                **{f"person_{entity}_id": ids for entity in groups},
            }
        ),
        **tables,
        time_period=YEAR,
    )


def test_deciles_rank_only_included_people_and_preserve_monthly_stock():
    mixed = Microsimulation(dataset=_rank_source())
    standalone = Microsimulation(dataset=_rank_source(include_outside=False))
    actual = mixed.calculate("spm_unit_income_decile", YEAR)
    expected = standalone.calculate("spm_unit_income_decile", YEAR)
    assert np.issubdtype(actual.dtype, np.floating)
    np.testing.assert_array_equal(actual[:3], expected)
    assert np.isnan(actual[3])
    assert np.all((expected >= 1) & (expected <= 10))
    np.testing.assert_array_equal(expected, np.floor(expected))
    assert len(np.unique(expected)) > 1, "The ranking fixture must distinguish incomes"
    for month in ("01", "07"):
        np.testing.assert_array_equal(
            mixed.calculate("spm_unit_income_decile", f"{YEAR}-{month}"), actual
        )


def test_all_outside_deciles_do_not_call_the_ranker(mixed_source, monkeypatch):
    from microdf import MicroSeries

    source = mixed_source.copy()
    source.spm_unit[STATUS] = "OUTSIDE"

    def forbidden(*args, **kwargs):
        raise AssertionError("An all-outside population has no ranks")

    monkeypatch.setattr(MicroSeries, "decile_rank", forbidden)
    result = Microsimulation(dataset=source).calculate("spm_unit_income_decile", YEAR)
    assert np.isnan(result).all()


@pytest.mark.parametrize("invalid", [np.nan, np.inf, -np.inf])
@pytest.mark.parametrize("variable", DISTRIBUTION_OUTPUTS)
def test_included_distribution_income_must_be_finite(mixed_source, invalid, variable):
    # Formula injection exercises the measurement guard: NaN stored inputs are
    # rejected earlier by Core and cannot prove that guard works.
    class spm_unit_net_income(Variable):
        def formula(spm_unit, period, parameters):
            return np.array([invalid, 0.0])

    class spm_unit_oecd_equiv_net_income(Variable):
        def formula(spm_unit, period, parameters):
            return np.array([invalid, 0.0])

    class InvalidIncome(Reform):
        def apply(self):
            self.update_variable(
                spm_unit_net_income
                if variable == "spm_unit_oecd_equiv_net_income"
                else spm_unit_oecd_equiv_net_income
            )

    simulation = Microsimulation(dataset=mixed_source, reform=InvalidIncome)
    with pytest.raises(SPMInputError) as error:
        simulation.calculate(variable, YEAR)
    assert error.value.code == "SPM_MEASUREMENT_INVALID"


@pytest.mark.parametrize("status", ["INCLUDED", "OUTSIDE", "UNRESOLVED"])
def test_explicit_annual_source_status_can_override_its_fallback(mixed_source, status):
    simulation = Microsimulation(dataset=mixed_source)
    simulation.set_input(STATUS, YEAR, [status, status])
    assert list(simulation.calculate(STATUS, YEAR)) == [status, status]


@pytest.mark.parametrize("problem", ["geography", "composition"])
def test_explicit_inclusion_preserves_canonical_input_validation(mixed_source, problem):
    source = mixed_source.copy()
    source.spm_unit[STATUS] = "INCLUDED"
    if problem == "geography":
        source.person["age"] = [40, 8, 40]
        expected_code = "SPM_GEOGRAPHY_REQUIRED"
    else:
        source.household["county_fips"] = ["06037", "36061"]
        expected_code = "SPM_COMPOSITION_REQUIRED"
    with pytest.raises(SPMInputError) as error:
        Microsimulation(dataset=source).calculate("spm_unit_spm_threshold", YEAR)
    assert error.value.code == expected_code


@pytest.mark.parametrize(
    "module_name,factory_name",
    [
        (
            "congress.tlaib.boost.boost_middle_class_tax_credit",
            "create_boost_middle_class_tax_credit",
        ),
        ("congress.tlaib.end_child_poverty_act", "create_end_child_poverty_act"),
        (
            "congress.tlaib.economic_dignity_for_all_agenda.edaa_end_child_poverty_act",
            "create_ecpa_only",
        ),
        ("states.tx.rebate.tx_rebate", "create_tx_rebate"),
    ],
)
@pytest.mark.parametrize("abolish_housing", [False, True])
def test_contributed_spm_benefits_refuse_unresolved_scope_before_housing_branch(
    mixed_source, monkeypatch, module_name, factory_name, abolish_housing
):
    source = mixed_source.copy()
    source.spm_unit[STATUS] = ["INCLUDED", "UNRESOLVED"]
    source.spm_unit["hud_hap"] = 0.0
    factory = getattr(
        import_module(f"policyengine_us.reforms.{module_name}"), factory_name
    )
    reform = (
        factory(),
        {"gov.hud.abolition": {f"{YEAR}-01-01.{YEAR}-12-31": abolish_housing}},
    )

    def forbidden(*args, **kwargs):
        raise AssertionError("Unresolved scope must fail before provider execution")

    monkeypatch.setattr(PolicyEngineSPMProvider, "calculate_unit", forbidden)
    simulation = Microsimulation(dataset=source, reform=reform)
    assert np.isfinite(simulation.calculate("household_benefits", YEAR)).all()
    for name in ("spm_unit_benefits", "spm_unit_net_income"):
        with pytest.raises(SPMInputError) as error:
            simulation.calculate(name, YEAR)
        assert error.value.code == "SPM_UNIVERSE_REQUIRED"


@pytest.mark.parametrize("invalid", [np.nan, np.inf, -np.inf])
@pytest.mark.parametrize("variable", POVERTY_INDICATORS)
def test_included_poverty_resources_must_be_finite(mixed_source, invalid, variable):
    class spm_unit_net_income(Variable):
        def formula(spm_unit, period, parameters):
            return np.array([invalid, 0.0])

    class InvalidResources(Reform):
        def apply(self):
            self.update_variable(spm_unit_net_income)

    simulation = Microsimulation(dataset=mixed_source, reform=InvalidResources)
    with pytest.raises(SPMInputError) as error:
        simulation.calculate(variable, YEAR)
    assert error.value.code == "SPM_MEASUREMENT_INVALID"


@pytest.mark.parametrize("invalid", [np.nan, np.inf, -np.inf, 0.0, -1.0])
@pytest.mark.parametrize("variable", POVERTY_INDICATORS)
def test_included_poverty_thresholds_must_be_positive_and_finite(
    mixed_source, invalid, variable
):
    class spm_unit_spm_threshold(Variable):
        def formula(spm_unit, period, parameters):
            return np.array([invalid, np.nan])

    class InvalidThreshold(Reform):
        def apply(self):
            self.update_variable(spm_unit_spm_threshold)

    simulation = Microsimulation(dataset=mixed_source, reform=InvalidThreshold)
    with pytest.raises(SPMInputError) as error:
        simulation.calc(variable, period=YEAR)
    assert error.value.code == "SPM_MEASUREMENT_INVALID"


def test_outside_role_placeholders_preserve_measurements_and_ordinary_outcomes(
    mixed_source,
):
    """An outside role may change composition, but cannot change named outcomes."""
    false_source = mixed_source.copy()
    false_source.person.loc[false_source.person.person_id == 301, "age"] = 17
    true_source = false_source.copy()
    true_source.person.loc[
        true_source.person.person_id == 301, "is_spm_independent_minor_role"
    ] = True
    false_model = Microsimulation(dataset=false_source)
    true_model = Microsimulation(dataset=true_source)
    assert false_model.calc("spm_measurement_adults", period=YEAR).iloc[1] == 0
    assert true_model.calc("spm_measurement_adults", period=YEAR).iloc[1] == 1
    for variable in ALL_MEASUREMENTS:
        false_result = false_model.calc(variable, period=YEAR, map_to="person")
        true_result = true_model.calc(variable, period=YEAR, map_to="person")
        np.testing.assert_array_equal(false_result, true_result, err_msg=variable)
        assert false_result.isna().tolist() == [False, False, True], variable
        assert true_result.isna().tolist() == [False, False, True], variable
        assert false_result.count() == true_result.count() == 4, variable
        assert false_result.sum() == true_result.sum(), variable
        assert false_result.mean() == true_result.mean(), variable
    for variable in ORDINARY_OUTCOMES:
        false_result = false_model.calc(variable, period=YEAR, map_to="person")
        true_result = true_model.calc(variable, period=YEAR, map_to="person")
        np.testing.assert_array_equal(false_result, true_result, err_msg=variable)
        assert not false_result.isna().any(), variable
        assert false_result.count() == true_result.count() == 9, variable
        assert false_result.sum() == true_result.sum(), variable
        assert false_result.mean() == true_result.mean(), variable


def _county_type_collision_source(mixed_source):
    source = mixed_source.copy()
    source.household["state_code"] = ["NY", "NY"]
    # Both spell the same county after string conversion, but only the first
    # is a valid source input. The second belongs to an outside unit.
    source.household["county_fips"] = ["36061", 36061]
    return source


@pytest.mark.parametrize("simulation_type", [Simulation, Microsimulation])
def test_outside_numeric_county_does_not_poison_included_measurements(
    mixed_source, simulation_type
):
    source = _county_type_collision_source(mixed_source)
    simulation = simulation_type(dataset=source)
    standalone = simulation_type(dataset=_only_included(source))
    provider = simulation.tax_benefit_system.spm_forecast_provider
    original_types = provider._untyped_counties
    before = original_types.copy()
    assert before[(YEAR, "36061")] == "36061"

    for variable in MEASUREMENT_AMOUNTS[:6]:
        actual = simulation.calculate(variable, YEAR)
        expected = standalone.calculate(variable, YEAR)
        assert np.isfinite(actual[0]), variable
        assert actual[0] == expected[0], variable
        assert np.isnan(actual[1]), variable
        # Selection must use a private typing view, not mutate the original
        # receipt to forget the malformed outside input.
        assert provider._untyped_counties is original_types
        assert provider._untyped_counties == before

    # A selected provider view must still populate the simulation's original
    # cache and provenance, rather than strand them on a temporary provider.
    assert provider._amount_cache
    provenance = simulation.spm_provenance()
    assert set(provenance["years"]) == {str(YEAR)}
    assert provenance["geographies"]
    assert {
        receipt["county_assignment"]["county_fips"]
        for receipt in provenance["geographies"]
    } == {"36061"}


@pytest.mark.parametrize("simulation_type", [Simulation, Microsimulation])
def test_cached_valid_county_amount_does_not_accept_newly_included_numeric_county(
    mixed_source, simulation_type
):
    source = _county_type_collision_source(mixed_source)
    # Identical one-adult compositions ensure the numeric row would hit the
    # valid row's exact provider cache key if typing were checked too late.
    source.person = source.person.loc[source.person.person_id != 102].copy()
    source.person["age"] = [40, 40]
    source.marital_unit = source.marital_unit.loc[
        source.marital_unit.marital_unit_id != 102
    ].copy()
    source = source.copy()  # Rebuild the table tuple after replacing frames.
    simulation = simulation_type(dataset=source)
    provider = simulation.tax_benefit_system.spm_forecast_provider
    before = provider._untyped_counties.copy()
    for variable in MEASUREMENT_AMOUNTS[:6]:
        values = simulation.calculate(variable, YEAR)
        assert np.isfinite(values[0]) and np.isnan(values[1]), variable
    assert (YEAR, 1, 0, "renter", "36061") in provider._amount_cache

    simulation.set_input(STATUS, YEAR, ["INCLUDED", "INCLUDED"])
    for variable in MEASUREMENT_AMOUNTS[:6]:
        # Core's explicit input API does not invalidate dependent holders.
        # Recalculate the output while deliberately retaining the provider memo.
        simulation.delete_arrays(variable, YEAR)
        with pytest.raises(SPMInputError) as error:
            simulation.calculate(variable, YEAR)
        assert error.value.code == "SPM_GEOGRAPHY_REQUIRED", variable
    assert provider._untyped_counties == before


@pytest.mark.parametrize("simulation_type", [Simulation, Microsimulation])
def test_unassisted_included_numeric_county_does_not_poison_assisted_housing_cap(
    mixed_source, simulation_type
):
    source = _county_type_collision_source(mixed_source)
    source.person["age"] = [40, 8, 40]
    source.spm_unit[STATUS] = "INCLUDED"
    source.spm_unit["hud_hap"] = [30_000.0, 0.0]
    simulation = simulation_type(dataset=source)
    standalone = simulation_type(dataset=_only_included(source))
    provider = simulation.tax_benefit_system.spm_forecast_provider
    before = provider._untyped_counties.copy()

    cap = simulation.calculate("spm_unit_capped_housing_subsidy", YEAR)
    expected = standalone.calculate("spm_unit_capped_housing_subsidy", YEAR)
    assert np.isfinite(cap[0]) and cap[0] > 0
    np.testing.assert_array_equal(cap, [expected[0], 0.0])
    assert provider._untyped_counties == before
    # Only the cap may ignore this unassisted unit's geography: a threshold
    # measurement still selects every included unit and must reject its type.
    with pytest.raises(SPMInputError) as error:
        simulation.calculate("spm_unit_spm_threshold", YEAR)
    assert error.value.code == "SPM_GEOGRAPHY_REQUIRED"


@pytest.mark.parametrize("new_status", ["OUTSIDE", "UNRESOLVED"])
def test_scope_input_mutation_cannot_reuse_cached_measurements(
    mixed_source, new_status
):
    simulation = Microsimulation(dataset=mixed_source)
    outputs = (
        "spm_unit_spm_threshold",
        "person_in_poverty",
        "spm_unit_income_decile",
    )
    for variable in outputs:
        cached = simulation.calc(variable, period=YEAR, map_to="person")
        assert cached.count() == 4, variable
        assert cached.isna().tolist() == [False, False, True], variable
    ordinary = simulation.calc("household_net_income", period=YEAR, map_to="person")
    simulation.set_input(STATUS, YEAR, [new_status, "OUTSIDE"])
    for variable in outputs:
        if new_status == "UNRESOLVED":
            with pytest.raises(SPMInputError) as error:
                simulation.calc(variable, period=YEAR, map_to="person")
            assert error.value.code == "SPM_UNIVERSE_REQUIRED", variable
        else:
            result = simulation.calc(variable, period=YEAR, map_to="person")
            assert result.isna().all(), variable
            assert result.count() == 0, variable
    np.testing.assert_array_equal(
        simulation.calc("household_net_income", period=YEAR, map_to="person"),
        ordinary,
    )


def test_observed_role_input_mutation_cannot_reuse_cached_composition(mixed_source):
    source = mixed_source.copy()
    source.person["age"] = [40, 8, 17]
    source.person["is_spm_independent_minor_role"] = [False, False, True]
    source.household["county_fips"] = ["06037", "36061"]
    source.spm_unit[STATUS] = "INCLUDED"
    simulation = Microsimulation(dataset=source)
    assert simulation.calc("spm_measurement_adults", period=YEAR).tolist() == [1, 1]
    outputs = (
        "spm_unit_spm_threshold",
        "person_in_poverty",
        "spm_unit_income_decile",
    )
    for variable in outputs:
        assert not simulation.calc(variable, period=YEAR).isna().any(), variable
    simulation.set_input("is_spm_independent_minor_role", "eternity", [False] * 3)
    assert simulation.calc("spm_measurement_adults", period=YEAR).tolist() == [1, 0]
    for variable in outputs:
        with pytest.raises(SPMInputError) as error:
            simulation.calc(variable, period=YEAR)
        assert error.value.code == "SPM_COMPOSITION_REQUIRED", variable


def _outcome_snapshot(simulation, variables):
    snapshot = {}
    for variable in variables:
        result = simulation.calc(variable, period=YEAR, map_to="person")
        # Detach fixture values, while computing every weighted statistic on
        # the original MicroSeries. Later cache mutations cannot rewrite this.
        snapshot[variable] = {
            "values": result.tolist(),
            "count": result.count(),
            "sum": result.sum(),
            "mean": result.mean(),
        }
    return snapshot


def _assert_outcome_snapshot(simulation, snapshot):
    for variable, expected in snapshot.items():
        actual = simulation.calc(variable, period=YEAR, map_to="person")
        np.testing.assert_array_equal(actual, expected["values"], err_msg=variable)
        assert actual.count() == expected["count"], variable
        assert actual.sum() == expected["sum"], variable
        assert actual.mean() == expected["mean"], variable


@pytest.mark.parametrize("source_input", [STATUS, "is_spm_independent_minor_role"])
def test_unchanged_source_assignment_preserves_inputs_and_all_outcomes(
    mixed_source, source_input
):
    original_tables = [table.copy(deep=True) for table in mixed_source.tables]
    simulation = Microsimulation(dataset=mixed_source)
    outcomes = _outcome_snapshot(simulation, (*ALL_MEASUREMENTS, *ORDINARY_OUTCOMES))
    source_names = (
        STATUS,
        "is_spm_independent_minor_role",
        "age",
        "employment_income",
        "county_fips",
        "hud_hap",
        "hud_ttp",
    )
    original_inputs = {
        name: simulation.calc(name, period=YEAR).tolist() for name in source_names
    }
    source_period = YEAR if source_input == STATUS else "eternity"
    simulation.set_input(source_input, source_period, original_inputs[source_input])
    for name, expected in original_inputs.items():
        assert simulation.calc(name, period=YEAR).tolist() == expected, name
    _assert_outcome_snapshot(simulation, outcomes)
    for before, after in zip(original_tables, mixed_source.tables, strict=True):
        pd.testing.assert_frame_equal(before, after)


def test_branch_scope_mutation_preserves_parent_and_sibling_snapshots(mixed_source):
    original_tables = [table.copy(deep=True) for table in mixed_source.tables]
    parent = Microsimulation(dataset=mixed_source)
    outputs = (
        "spm_unit_spm_threshold",
        "person_in_poverty",
        "spm_unit_income_decile",
        *ORDINARY_OUTCOMES,
    )
    snapshot = _outcome_snapshot(parent, outputs)
    # Share policy parameters; these tiny branches must not clone the full
    # parameter tree merely to change one observed source declaration.
    target = parent.get_branch("scope_mutation_target", clone_system=False)
    sibling = parent.get_branch("scope_mutation_sibling", clone_system=False)
    _assert_outcome_snapshot(target, snapshot)
    _assert_outcome_snapshot(sibling, snapshot)
    target.set_input(STATUS, YEAR, ["OUTSIDE", "OUTSIDE"])
    assert list(target.calc(STATUS, period=YEAR)) == ["OUTSIDE", "OUTSIDE"]
    for variable in outputs[:3]:
        result = target.calc(variable, period=YEAR, map_to="person")
        assert result.isna().all(), variable
        assert result.count() == 0, variable
    _assert_outcome_snapshot(
        target, {name: snapshot[name] for name in ORDINARY_OUTCOMES}
    )
    for untouched in (parent, sibling):
        assert list(untouched.calc(STATUS, period=YEAR)) == ["INCLUDED", "OUTSIDE"]
        _assert_outcome_snapshot(untouched, snapshot)
    for before, after in zip(original_tables, mixed_source.tables, strict=True):
        pd.testing.assert_frame_equal(before, after)


@pytest.mark.parametrize(
    "variable,period,value,expected_calls",
    [
        (STATUS, YEAR, ["OUTSIDE", "OUTSIDE"], 1),
        ("is_spm_independent_minor_role", "eternity", [False, False, True], 1),
        ("employment_income", YEAR, [7_000.0, 0.0, 0.0], 0),
        ("county_fips", YEAR, ["36061", "06037"], 0),
    ],
    ids=["scope", "role", "ordinary-income", "ordinary-county"],
)
def test_full_cache_invalidation_is_limited_to_spm_source_assignments(
    mixed_source, monkeypatch, variable, period, value, expected_calls
):
    """The new source contract must not widen ordinary set_input semantics."""
    simulation = Microsimulation(dataset=mixed_source)
    original = simulation._invalidate_all_caches
    calls = []

    def tracked_invalidation():
        calls.append(True)
        return original()

    monkeypatch.setattr(simulation, "_invalidate_all_caches", tracked_invalidation)
    simulation.set_input(variable, period, value)
    assert len(calls) == expected_calls
