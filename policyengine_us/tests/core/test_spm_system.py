"""Construction and dataset contracts that require the Python simulation API."""

import ast
import hashlib
import inspect
import json
from pathlib import Path
import re
import textwrap

import numpy as np
import pandas as pd
import pytest
from policyengine_core.reforms import Reform
from policyengine_core.periods import YEAR
from policyengine_core.variables import Variable
from spm_calculator.errors import SPMInputError
from spm_calculator.policyengine_adapter import FORMULA_OWNED_INPUTS

from policyengine_us import Microsimulation, Simulation
from policyengine_us.data.dataset_schema import USMultiYearDataset, USSingleYearDataset
from policyengine_us.entities import Person
from policyengine_us.spm import (
    DERIVED_POVERTY_OUTPUTS,
    REJECTED_DATASET_INPUTS,
    SPM_DISTRIBUTION_OUTPUTS,
    create_spm_provider,
    is_county_fips,
)
from policyengine_us import system as system_module
from policyengine_us.system import (
    DEFAULT_DATASET,
    DEFAULT_DATASET_SHA256,
    _file_sha256,
    _resolve_dataset_path,
    _verify_default_dataset,
    system,
)


def single_person_situation():
    return {
        "people": {"person": {"age": {2024: 40}}},
        "households": {
            "household": {"members": ["person"], "county_fips": {2024: "06037"}}
        },
    }


class household_market_income(Variable):
    # Partial reform variables inherit their entity, period and dtype from the
    # baseline variable. Cloning must not call this class without that baseline.
    def formula(household, period, parameters):
        return household.filled_array(123)


class UserReform(Reform):
    def apply(self):
        self.update_variable(household_market_income)
        self.neutralize_variable("income_tax")


@pytest.mark.parametrize("reform_wrapper", [False, True])
def test_chosen_system_and_simulation_clones_preserve_user_reform(reform_wrapper):
    chosen = system.clone()
    if reform_wrapper:
        chosen = UserReform(chosen)
    else:
        UserReform.apply(chosen)
    original_config = chosen.spm_forecast_provider
    situation = single_person_situation()
    situation["people"]["person"]["employment_income"] = {2024: 50_000}
    simulation = Simulation(
        tax_benefit_system=chosen,
        situation=situation,
        spm={"geography_kind": "national"},
    )
    assert chosen.spm_forecast_provider is original_config
    assert chosen.spm_forecast_provider.geography_kind == "county"
    assert simulation.calculate("household_market_income", 2024)[0] == 123
    assert simulation.calculate("income_tax", 2024)[0] == 0
    assert simulation.tax_benefit_system.variables["income_tax"].is_neutralized
    simulation.calculate("spm_unit_spm_threshold", 2024)

    clone = simulation.clone()
    clone.delete_arrays("household_market_income")
    assert clone.calculate("household_market_income", 2024)[0] == 123
    assert clone.tax_benefit_system.variables["income_tax"].is_neutralized
    assert clone.calculate("income_tax", 2024)[0] == 0
    assert clone.spm_provenance() == simulation.spm_provenance()
    clone.tax_benefit_system.variables["income_tax"].is_neutralized = False
    clone.delete_arrays("income_tax")
    assert clone.calculate("income_tax", 2024)[0] == 4_016
    assert simulation.calculate("income_tax", 2024)[0] == 0
    assert simulation.tax_benefit_system.variables["income_tax"].is_neutralized
    assert chosen.variables["income_tax"].is_neutralized


@pytest.mark.parametrize("simulation_type", [Simulation, Microsimulation])
def test_reform_baseline_and_clones_calculate_original_tax(simulation_type):
    if simulation_type is Simulation:
        situation = single_person_situation()
        situation["people"]["person"]["employment_income"] = {2024: 50_000}
        inputs = {"situation": situation}
    else:
        source = small_dataset()
        source.person["age"] = [40, 40]
        source.person["employment_income"] = [50_000, 50_000]
        inputs = {"dataset": source}
    config = {"geography_kind": "national"}
    ordinary = simulation_type(**inputs, spm=config)
    changed = simulation_type(**inputs, reform=UserReform, spm=config)

    np.testing.assert_array_equal(ordinary.calculate("income_tax", 2024), 4_016)
    np.testing.assert_array_equal(changed.calculate("income_tax", 2024), 0)
    np.testing.assert_array_equal(changed.baseline.calculate("income_tax", 2024), 4_016)
    np.testing.assert_array_equal(
        changed.baseline.calculate("household_market_income", 2024), 50_000
    )
    np.testing.assert_array_equal(
        changed.calculate("household_market_income", 2024), 123
    )

    for original, expected in ((changed, 0), (changed.baseline, 4_016)):
        clone = original.clone()
        np.testing.assert_array_equal(clone.calculate("income_tax", 2024), expected)
        clone.delete_arrays("income_tax")
        np.testing.assert_array_equal(clone.calculate("income_tax", 2024), expected)
        for population in clone.populations.values():
            assert population.entity._tax_benefit_system is clone.tax_benefit_system
            for name, holder in population._holders.items():
                assert holder.variable is clone.tax_benefit_system.variables[name]
                assert holder.simulation is clone
        assert clone.tax_benefit_system.simulation is clone


def _parameter_fingerprint(system):
    """Digest every authored parameter value, so a shared-tree edit is visible."""
    digest = hashlib.sha256()
    for parameter in system.parameters.get_descendants():
        values = getattr(parameter, "values_list", None)
        if values is None:
            continue
        digest.update(parameter.name.encode())
        for value_at_instant in values:
            digest.update(
                f"|{value_at_instant.instant_str}={value_at_instant.value}".encode()
            )
    return digest.hexdigest()


def test_ordinary_simulation_shares_default_policy_state():
    """A plain household simulation must not rebuild the shipped policy.

    Core's TaxBenefitSystem.clone() rebuilds the parameter tree node by node and
    empties both at-instant caches, and this country deep-copies every variable
    on top, so cloning per request would make each household API call rebuild
    the at-instant tree for every period it touches. Nothing distinguishes an
    ordinary simulation's policy from the shared instance's, so it shares the
    tree and reuses the variable objects, and only its receipts and its own
    variable registry are private.
    """
    parameters_before = _parameter_fingerprint(system)
    variables_before = {name: id(value) for name, value in system.variables.items()}
    provider_before = system.spm_forecast_provider

    simulation = Simulation(situation=single_person_situation())
    policy = simulation.tax_benefit_system

    # Same parameter tree and the same warm at-instant caches: no clone ran.
    assert policy is not system
    assert policy.parameters is system.parameters
    assert policy._parameters_at_instant_cache is system._parameters_at_instant_cache
    # Entities are private and bound to this simulation's own registry: an
    # entity resolves variable names through the system it is bound to, so
    # sharing the shared instance's entities would send every holder lookup to
    # the shared registry.
    assert policy.entities is not system.entities
    assert {entity.key for entity in policy.entities} == {
        entity.key for entity in system.entities
    }
    for entity in policy.entities:
        assert entity._tax_benefit_system is policy
    for entity in system.entities:
        assert entity._tax_benefit_system is system
    # One object per key, so rebinding one reaches every reader of it.
    by_key = {entity.key: entity for entity in policy.entities}
    assert policy.person_entity is by_key[policy.person_entity.key]
    assert all(entity is by_key[entity.key] for entity in policy.group_entities)
    # A private registry, holding the shared instance's own variable objects.
    assert policy.variables is not system.variables
    assert (
        policy.variables["household_net_income"]
        is system.variables["household_net_income"]
    )
    rebound = {
        name
        for name, variable in policy.variables.items()
        if variable is not system.variables[name]
    }
    # Only the structural reform re-applied at this simulation's start instant
    # rebinds a name, and it rebinds in the private registry.
    assert len(rebound) < 10, sorted(rebound)

    # Nothing reached the shared instance.
    assert {name: id(value) for name, value in system.variables.items()} == (
        variables_before
    )
    assert _parameter_fingerprint(system) == parameters_before
    assert system.spm_forecast_provider is provider_before

    # Receipts remain private per simulation.
    simulation.calculate("spm_unit_spm_threshold", 2024)
    assert set(simulation.spm_provenance()["years"]) == {"2024"}
    assert system.spm_forecast_provider.provenance()["years"] == {}
    later = Simulation(situation=single_person_situation())
    assert later.spm_provenance()["years"] == {}
    # The second simulation reads the at-instant tree the first one built.
    assert system.parameters._at_instant_cache
    assert (
        later.tax_benefit_system.parameters._at_instant_cache
        is system.parameters._at_instant_cache
    )


def test_applying_reform_to_calculated_clone_preserves_original_tax():
    situation = single_person_situation()
    situation["people"]["person"]["employment_income"] = {2024: 50_000}
    original = Simulation(situation=situation)
    assert original.calculate("income_tax", 2024)[0] == 4_016
    assert original.calculate("household_market_income", 2024)[0] == 50_000
    clone = original.clone()
    branch = clone.get_branch("shared_policy")
    isolated_branch = clone.get_branch("separate_policy", clone_system=True)
    clone.apply_reform(UserReform)
    assert clone.calculate("income_tax", 2024)[0] == 0
    assert clone.calculate("household_market_income", 2024)[0] == 123
    assert branch.calculate("income_tax", 2024)[0] == 0
    assert branch.calculate("household_market_income", 2024)[0] == 123
    assert (
        branch.get_holder("income_tax").variable
        is branch.tax_benefit_system.variables["income_tax"]
    )
    assert isolated_branch.calculate("income_tax", 2024)[0] == 4_016
    assert isolated_branch.calculate("household_market_income", 2024)[0] == 50_000
    clone.tax_benefit_system.variables["income_tax"].is_neutralized = False
    clone.delete_arrays("income_tax")
    assert clone.calculate("income_tax", 2024)[0] == 4_016
    assert original.calculate("income_tax", 2024)[0] == 4_016
    assert original.calculate("household_market_income", 2024)[0] == 50_000
    assert (
        clone.get_holder("income_tax").variable
        is clone.tax_benefit_system.variables["income_tax"]
    )


class clone_only_income(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Income input added only by the test reform"


class AddedInputReform(Reform):
    def apply(self):
        self.update_variable(clone_only_income)


def test_clone_can_add_a_variable_without_mutating_original():
    original = Simulation(situation=single_person_situation())
    clone = original.clone()
    branch = clone.get_branch("shared_policy")
    clone.apply_reform(AddedInputReform)
    clone.set_input("clone_only_income", 2024, [123])
    assert clone.calculate("clone_only_income", 2024)[0] == 123
    branch.set_input("clone_only_income", 2024, [456])
    assert branch.calculate("clone_only_income", 2024)[0] == 456
    assert clone.calculate("clone_only_income", 2024)[0] == 123
    assert "clone_only_income" not in original.tax_benefit_system.variables
    assert not any(key[0] == "clone_only_income" for key in original._user_input_keys)


def test_reform_only_input_does_not_leak_into_baseline_cache_invalidation():
    situation = single_person_situation()
    situation["people"]["person"].update(
        employment_income={2024: 50_000}, clone_only_income={2024: 123}
    )
    simulation = Simulation(situation=situation, reform=AddedInputReform)
    assert simulation.calculate("clone_only_income", 2024)[0] == 123
    baseline = simulation.baseline
    assert "clone_only_income" not in baseline.input_variables
    assert not any(key[0] == "clone_only_income" for key in baseline._user_input_keys)
    baseline.apply_reform(())
    assert baseline.calculate("income_tax", 2024)[0] == 4_016
    assert simulation.calculate("clone_only_income", 2024)[0] == 123


def test_new_simulation_from_calculated_system_starts_fresh_receipts():
    first = Simulation(situation=single_person_situation())
    first.calculate("spm_unit_spm_threshold", 2024)
    second = Simulation(first.tax_benefit_system, situation=single_person_situation())
    assert second.spm_config == first.spm_config
    assert second.spm_provenance()["years"] == {}
    second.calculate("spm_unit_spm_threshold", 2025)
    assert set(first.spm_provenance()["years"]) == {"2024"}
    assert set(second.spm_provenance()["years"]) == {"2025"}


def test_positional_reform_baseline_uses_selected_spm_configuration():
    simulation = Simulation(
        None,
        None,
        single_person_situation(),
        None,
        (),
        spm={"geography_kind": "national"},
    )
    assert simulation.baseline.spm_config == simulation.spm_config
    assert simulation.baseline.calculate("spm_unit_geographic_adjustment", 2024)[0] == 1
    assert simulation.spm_provenance()["years"] == {}


def test_shared_policy_branch_detaches_spm_receipts():
    simulation = Simulation(situation=single_person_situation())
    simulation.calculate("spm_unit_spm_threshold", 2024)
    branch = simulation.get_branch("spm_receipt_test")
    assert (
        branch.tax_benefit_system.variables is simulation.tax_benefit_system.variables
    )
    assert (
        branch.tax_benefit_system.parameters is simulation.tax_benefit_system.parameters
    )
    assert branch.tax_benefit_system.simulation is branch
    assert branch.spm_provenance() == simulation.spm_provenance()
    branch.calculate("spm_unit_spm_threshold", 2025)
    assert set(simulation.spm_provenance()["years"]) == {"2024"}
    assert set(branch.spm_provenance()["years"]) == {"2024", "2025"}


@pytest.mark.parametrize(
    "config",
    [
        {"forecast_path": "/tmp/forecast.json"},
        {"path": "/tmp/forecast.json"},
        {"as_of": "2022-01-01"},
        {"as_of": "2026-99-01"},
        {"geography_kind": "national", "geography_id": "06037"},
        {"geography_kind": "county", "geography_id": "06037"},
        {"geography_kind": "metro"},
        {"county_vintage": None},
    ],
)
def test_unsupported_public_configuration_fails(config):
    with pytest.raises(ValueError):
        create_spm_provider(config)


def test_as_of_config_and_receipts_are_serializable():
    simulation = Simulation(
        situation=single_person_situation(), spm={"as_of": "2026-09-09"}
    )
    simulation.calculate("spm_unit_spm_threshold", 2035)
    assert json.loads(json.dumps(simulation.spm_config))["as_of"] == "2026-09-09"
    assert set(json.loads(json.dumps(simulation.spm_provenance()))["years"]) == {"2035"}


class _HubResponse:
    """The minimum a Hugging Face HTTP error reads off its response."""

    headers = {}
    request = None


def _hub_failures():
    from huggingface_hub.errors import (
        LocalEntryNotFoundError,
        RevisionNotFoundError,
    )

    return [
        # What an unpublished build id actually produces: the Hub 404s and the
        # download then reports that the file is not in the local cache either.
        LocalEntryNotFoundError(
            "An error happened while trying to locate the file on the Hub and "
            "we cannot find the requested file"
        ),
        RevisionNotFoundError(
            "404 Client Error: Revision Not Found", response=_HubResponse()
        ),
    ]


@pytest.mark.parametrize("failure", _hub_failures(), ids=["offline", "revision"])
def test_unresolved_dataset_build_names_the_uri_it_could_not_resolve(
    failure, monkeypatch
):
    """A Hub failure must say which dataset the model was asked for.

    Both of these otherwise reach the caller with no mention of the URI, so an
    unpublished build id reads as a broken installation.
    """
    import huggingface_hub

    def missing(*args, **kwargs):
        raise failure

    monkeypatch.setattr(huggingface_hub, "hf_hub_download", missing)
    with pytest.raises(FileNotFoundError) as error:
        _resolve_dataset_path(DEFAULT_DATASET)
    message = str(error.value)
    assert DEFAULT_DATASET in message
    assert str(failure) in message
    assert error.value.__cause__ is failure


@pytest.mark.parametrize("simulation_type", [Simulation, Microsimulation])
@pytest.mark.parametrize(
    "counties",
    [
        # A legacy population file storing the CPS within-state code.
        [5, 1],
        # A county code whose decimal form is five digits, so only its type
        # distinguishes it from the documented input.
        [36_061, 36_061],
        # The same mistake for a state whose code carries a leading zero.
        [6_037, 6_037],
        [float("nan"), float("nan")],
    ],
    ids=["within_state", "five_digit_integer", "dropped_leading_zero", "missing"],
)
def test_non_text_county_column_requires_county_fips_however_it_is_spelled(
    simulation_type, counties
):
    """``county_fips`` is documented as a five-digit *string*.

    Core maps a ``str`` variable onto the numpy ``object`` dtype, so the model
    stores an integer column as integers, and every reader stringifies before
    asking the forecast provider. An integer county code for a state without a
    leading zero was therefore accepted silently, while the identical mistake
    for California was reported as an absent county.
    """
    source = small_dataset()
    source.household["county_fips"] = counties
    simulation = simulation_type(dataset=source)
    with pytest.raises(SPMInputError) as error:
        simulation.calculate("spm_unit_spm_threshold", 2024)
    assert error.value.code == "SPM_GEOGRAPHY_REQUIRED"
    assert "five-digit string" in str(error.value)
    assert 'geography_kind="national"' in str(error.value)
    # The same population computes once an SPM area is selected explicitly:
    # a caller who never asks for a county is never asked for one.
    national = simulation_type(dataset=source, spm={"geography_kind": "national"})
    assert np.all(national.calculate("spm_unit_spm_threshold", 2024) > 0)


def test_correcting_a_county_input_clears_its_rejection():
    """The record has to follow the input, not outlive it."""
    situation = single_person_situation()
    situation["households"]["household"]["county_fips"] = {2024: 36_061}
    simulation = Simulation(situation=situation)
    with pytest.raises(SPMInputError):
        simulation.calculate("spm_unit_spm_threshold", 2024)

    simulation.set_input("county_fips", 2024, ["36061"])

    assert simulation.calculate("spm_unit_spm_threshold", 2024)[0] > 0


def test_a_county_rejection_does_not_follow_the_system_to_a_new_simulation():
    """A new simulation reads its own inputs; only a clone keeps these."""
    situation = single_person_situation()
    situation["households"]["household"]["county_fips"] = {2024: 36_061}
    mistyped = Simulation(situation=situation)
    with pytest.raises(SPMInputError):
        mistyped.calculate("spm_unit_spm_threshold", 2024)

    # The same county, sent correctly: the lender's record of its own mistake
    # must not reject it.
    situation = single_person_situation()
    situation["households"]["household"]["county_fips"] = {2024: "36061"}
    correct = Simulation(
        tax_benefit_system=mistyped.tax_benefit_system, situation=situation
    )
    assert correct.calculate("spm_unit_spm_threshold", 2024)[0] > 0
    with pytest.raises(SPMInputError):
        mistyped.clone().calculate("spm_unit_spm_threshold", 2024)


def test_a_reform_simulations_baseline_arm_rejects_the_same_county_input():
    """Core hands the baseline arm a provider that never sees an input."""
    situation = single_person_situation()
    situation["households"]["household"]["county_fips"] = {2024: 36_061}
    simulation = Simulation(
        situation=situation,
        reform=Reform.from_dict(
            {"gov.irs.credits.ctc.amount.base[0].amount": {"2024": 0}}
        ),
    )
    for arm in (simulation, simulation.baseline):
        with pytest.raises(SPMInputError) as error:
            arm.calculate("spm_unit_spm_threshold", 2024)
        assert error.value.code == "SPM_GEOGRAPHY_REQUIRED"


def test_a_national_selection_records_no_county_input_types():
    """Nothing will ask that provider for a county, so nothing is scanned."""
    source = small_dataset()
    source.household["county_fips"] = [36_061, 36_061]
    national = Microsimulation(dataset=source, spm={"geography_kind": "national"})
    provider = national.tax_benefit_system.spm_forecast_provider
    assert provider._untyped_counties == {}
    assert np.all(national.calculate("spm_unit_spm_threshold", 2024) > 0)


def test_text_county_column_still_resolves_its_county():
    source = small_dataset()
    source.household["county_fips"] = ["06037", "36061"]
    simulation = Microsimulation(dataset=source)
    assert np.all(simulation.calculate("spm_unit_spm_threshold", 2024) > 0)
    assert len(simulation.spm_provenance()["geographies"]) == 2


@pytest.mark.parametrize(
    ("value", "accepted"),
    [
        ("06037", True),
        (b"06037", True),
        (np.str_("36061"), True),
        (np.bytes_(b"36061"), True),
        ("6037", False),
        ("", False),
        ("360610", False),
        (36_061, False),
        (np.int64(36_061), False),
        (36_061.0, False),
        (float("nan"), False),
        (None, False),
        (True, False),
    ],
)
def test_county_fips_accepts_five_digit_text_only(value, accepted):
    assert is_county_fips(value) is accepted


def small_dataset():
    groups = ("household", "tax_unit", "spm_unit", "family", "marital_unit")
    return USSingleYearDataset(
        person=pd.DataFrame(
            {
                "person_id": [1, 2],
                "age": [16, 40],
                "is_spm_independent_minor_role": [True, False],
                **{f"person_{entity}_id": [1, 2] for entity in groups},
            }
        ),
        household=pd.DataFrame(
            {
                "household_id": [1, 2],
                "county_fips": ["06037", "36061"],
                "household_weight": [1.0, 1.0],
            }
        ),
        # These two deliberate household units are included for this synthetic
        # year's measurements. Real/default population files are not relabelled.
        spm_unit=pd.DataFrame(
            {
                "spm_unit_id": [1, 2],
                "spm_unit_spm_universe_status": ["INCLUDED", "INCLUDED"],
            }
        ),
        **{
            entity: pd.DataFrame({f"{entity}_id": [1, 2]})
            for entity in groups
            if entity not in {"household", "spm_unit"}
        },
        time_period=2024,
    )


def test_positional_microsimulation_dataset_uses_country_interception():
    source = small_dataset()
    simulation = Microsimulation(None, None, None, source)
    assert isinstance(simulation.dataset, USMultiYearDataset)
    assert simulation.calculate("spm_measurement_adults", 2024).tolist() == [1, 1]


@pytest.mark.parametrize("simulation_type", [Simulation, Microsimulation])
def test_dataset_roles_receipts_and_formula_owned_rejection_preserve_source(
    simulation_type,
):
    source = small_dataset()
    before = [frame.copy(deep=True) for frame in source.tables]
    simulation = simulation_type(dataset=source)
    simulation.set_input(variable_name="age", period=2024, value=[16, 40])
    assert simulation.calculate("spm_measurement_adults", 2024).tolist() == [1, 1]
    assert simulation.calculate("spm_unit_count_adults", 2024).tolist() == [0, 1]
    assert np.all(simulation.calculate("spm_unit_spm_threshold", 2024) > 0)
    assert len(simulation.spm_provenance()["geographies"]) == 2
    json.dumps(simulation.spm_provenance())
    for name in REJECTED_DATASET_INPUTS:
        with pytest.raises(ValueError, match="formula-owned SPM output"):
            simulation.set_input(variable_name=name, period=2024, value=[1.0, 1.0])
    for original, current in zip(before, source.tables):
        pd.testing.assert_frame_equal(original, current)


@pytest.mark.parametrize("dataset_format", ["single", "multi", "hdfstore"])
def test_microsimulation_rejects_stored_measurements_without_mutating_dataset(
    dataset_format, tmp_path
):
    source = small_dataset()
    source.spm_unit["spm_unit_spm_threshold"] = [100.0, 200.0]
    before = [frame.copy(deep=True) for frame in source.tables]
    if dataset_format == "multi":
        dataset = USMultiYearDataset(datasets=[source])
    elif dataset_format == "hdfstore":
        path = tmp_path / "spm_input.h5"
        source.save(path)
        content = path.read_bytes()
        dataset = str(path)
    else:
        dataset = source
    with pytest.raises(ValueError, match="formula-owned SPM output"):
        Microsimulation(dataset=dataset)
    for original, current in zip(before, source.tables):
        pd.testing.assert_frame_equal(original, current)
    if dataset_format == "hdfstore":
        assert path.read_bytes() == content


@pytest.mark.parametrize(
    "name", sorted(DERIVED_POVERTY_OUTPUTS | SPM_DISTRIBUTION_OUTPUTS)
)
def test_dataset_storing_a_derived_poverty_output_is_refused(name):
    """A poverty alias the calculator does not own must still be refused.

    ``FORMULA_OWNED_INPUTS`` stops at the calculator's own outputs, so a
    dataset supplying ``in_poverty=[False, False]`` was accepted unchanged
    while every unit in the population sat below its threshold: the poverty
    calculation documented in ``docs/usage/microsimulation.md`` reported 0%
    and ``spm_unit_is_in_spm_poverty`` reported 100% for the same population.
    """
    variable = system.variables[name]
    source = small_dataset()
    table = getattr(source, variable.entity.key)
    table[name] = [False, False] if variable.value_type == bool else [0.0, 0.0]
    before = [frame.copy(deep=True) for frame in source.tables]
    with pytest.raises(ValueError) as error:
        Microsimulation(dataset=source)
    message = str(error.value)
    assert f"formula-owned SPM output {name}" in message
    assert "Use primitive inputs" in message
    for original, current in zip(before, source.tables):
        pd.testing.assert_frame_equal(original, current)


def test_accepted_population_publishes_one_poverty_rate():
    """The two published indicators agree once the aliases cannot be stored."""
    simulation = Microsimulation(dataset=small_dataset())
    np.testing.assert_array_equal(
        simulation.calculate("in_poverty", 2024),
        simulation.calculate("spm_unit_is_in_spm_poverty", 2024),
    )
    np.testing.assert_array_equal(
        simulation.calculate("in_deep_poverty", 2024),
        simulation.calculate("spm_unit_is_in_deep_spm_poverty", 2024),
    )


def test_rejection_set_extends_rather_than_replaces_the_calculator_contract():
    for name in FORMULA_OWNED_INPUTS:
        assert name in REJECTED_DATASET_INPUTS
    for name in DERIVED_POVERTY_OUTPUTS | SPM_DISTRIBUTION_OUTPUTS:
        # A rejected name must be computed, never a legitimate stored input.
        assert name in REJECTED_DATASET_INPUTS
        assert system.variables[name].formula is not None
    assert SPM_DISTRIBUTION_OUTPUTS == {
        "spm_unit_oecd_equiv_net_income",
        "spm_unit_income_decile",
    }


ENTITY_KEYS = frozenset(
    {"person", "marital_unit", "tax_unit", "family", "spm_unit", "household"}
)
# policyengine-core helpers that name the variables they read as string
# literals, exactly as an entity call does, so the constant scan below sees
# their reads too (policyengine_core/commons/formulas.py: for_each_variable
# and the aggregators built on it).
NAME_LISTING_HELPERS = frozenset(
    {"add", "and_", "or_", "max_", "min_", "for_each_variable", "sum_of_variables"}
)


def _static_variable_reads(variable):
    """Variable names a registered variable reads, or None when not static.

    Over-collects rather than under-collects: every string constant in the
    class body that names a registered variable counts, so a helper this scan
    does not model cannot make a variable look like a pure function of the
    poverty chain when it is not.

    A formula is only trusted when its reads are visibly named — through an
    entity call or a name-listing helper. A variable with no formula at all is
    fully described by its ``adds``/``subtracts`` list, which is how most of
    the poverty chain is written: ``poverty_line`` is ``adds =
    ["spm_unit_spm_threshold"]`` and nothing else. Requiring an entity call of
    those too discarded 884 of the system's variables, this measurement's own
    aliases among them, leaving the closure below blind to the very idiom the
    next alias would most likely use.
    """
    for attribute in ("adds", "subtracts"):
        if isinstance(getattr(variable, attribute, None), str):
            # A parameter path: its contents are not statically known here.
            return None
    reads = {
        item
        for attribute in ("adds", "subtracts")
        for item in (getattr(variable, attribute, None) or [])
    }
    try:
        source = textwrap.dedent(inspect.getsource(type(variable)))
    except (OSError, TypeError):
        # Calculator-built variables have no country source file.
        return None
    tree = ast.parse(source)
    named_reads = False
    has_formula = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("formula"):
                has_formula = True
        if isinstance(node, ast.Call):
            function = node.func
            name = getattr(function, "id", None) or getattr(function, "attr", None)
            if name in ENTITY_KEYS or name in NAME_LISTING_HELPERS:
                named_reads = True
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and node.value in system.variables
        ):
            reads.add(node.value)
    if has_formula and not named_reads:
        # A formula reaching for its inputs some other way; what it reads is
        # not knowable from the source.
        return None
    return reads - {variable.name}


def test_every_pure_function_of_the_poverty_chain_is_rejected():
    """The rejection set is closed: no further alias can be stored.

    A variable whose every read is already rejected and which reads at least
    one threshold or poverty output is another name for the same measurement.
    ``in_poverty`` was exactly that, and this closure is what stops the next
    one from shipping unpoliced.
    """
    chain = {
        name
        for name in REJECTED_DATASET_INPUTS
        if "poverty" in name or "threshold" in name or name in SPM_DISTRIBUTION_OUTPUTS
    }
    unrejected_aliases = []
    checked = []
    for name, variable in sorted(system.variables.items()):
        reads = _static_variable_reads(variable)
        if not reads or not reads <= REJECTED_DATASET_INPUTS or not reads & chain:
            continue
        checked.append(name)
        if name not in REJECTED_DATASET_INPUTS:
            unrejected_aliases.append(f"{name} reads {sorted(reads)}")
    assert not unrejected_aliases, (
        "These variables are pure functions of rejected SPM poverty outputs "
        "but a dataset may still store them; add them to "
        "DERIVED_POVERTY_OUTPUTS in policyengine_us/spm.py:\n"
        + "\n".join(unrejected_aliases)
    )
    # Guard the guard: a scan that silently matched nothing proves nothing.
    assert set(DERIVED_POVERTY_OUTPUTS) <= set(checked)
    # These distribution outputs also read scope/weights, so they are not pure
    # aliases captured by the subset scan. Their names must still be rejected
    # explicitly, and extending the chain above covers aliases of either one.
    assert SPM_DISTRIBUTION_OUTPUTS <= REJECTED_DATASET_INPUTS


@pytest.fixture
def decoy_default_dataset(monkeypatch, tmp_path):
    """Resolve the default URI to a valid but uncertified build.

    The decoy loads and calculates, so anything that rejects it rejects it on
    content rather than on shape.
    """
    path = tmp_path / "decoy.h5"
    small_dataset().save(path)
    monkeypatch.setattr(
        system_module,
        "_resolve_dataset_path",
        lambda dataset_str: str(path),
    )
    return path


def test_default_dataset_rejects_content_that_is_not_the_certified_build(
    decoy_default_dataset,
):
    """A moved build id must fail loudly instead of changing every result.

    The default pins a Hugging Face tag, which is a mutable pointer: without
    this check, re-tagging the repository silently substitutes another
    schema-valid population.
    """
    with pytest.raises(ValueError) as error:
        Microsimulation()
    message = str(error.value)
    assert DEFAULT_DATASET in message
    assert str(decoy_default_dataset) in message
    assert DEFAULT_DATASET_SHA256 in message
    assert _file_sha256(decoy_default_dataset) in message


def test_default_dataset_accepts_the_certified_digest(
    decoy_default_dataset, monkeypatch
):
    """The check passes exactly the certified bytes and obstructs nothing else."""
    monkeypatch.setattr(
        system_module,
        "DEFAULT_DATASET_SHA256",
        _file_sha256(decoy_default_dataset),
    )
    simulation = Microsimulation()
    assert simulation.calculate("spm_measurement_adults", 2024).tolist() == [1, 1]


def test_explicit_dataset_argument_is_not_content_checked(decoy_default_dataset):
    """A caller naming its own artifact owns that artifact's provenance."""
    simulation = Microsimulation(dataset=str(decoy_default_dataset))
    assert simulation.calculate("spm_measurement_adults", 2024).tolist() == [1, 1]


DEFAULT_BUILD_SECTION = "## Default population build"


def documented_default_build():
    """The default build's URI and content hash, read from `docs/spm.md`.

    The digest is a bare 64-character constant in `system.py` with no other
    occurrence in the repository, and the two tests that exercise the check
    substitute their own value for it, so a silent edit to the constant would
    pass the suite. `docs/spm.md` carries the value a human can compare with
    the producer's receipt and with the bytes the Hugging Face tag serves;
    this reads it back so the record and the constant cannot drift apart.
    """
    repository = Path(__file__).resolve().parents[3]
    if not (repository / "pyproject.toml").exists():
        pytest.skip("Not a source checkout: docs/ ships with the repository only.")
    document = (repository / "docs" / "spm.md").read_text(encoding="utf-8")
    assert DEFAULT_BUILD_SECTION in document, (
        f"docs/spm.md no longer has a '{DEFAULT_BUILD_SECTION}' section "
        "recording the default build's URI and content hash."
    )
    section = document.split(DEFAULT_BUILD_SECTION, 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"`(hf://[^`]+)`", section)), set(
        re.findall(r"`sha256:([0-9a-f]{64})`", section)
    )


def test_documented_default_build_matches_the_shipped_constants():
    """One edited side of the default-build record must fail, not ship."""
    uris, digests = documented_default_build()
    assert uris == {DEFAULT_DATASET}, (
        "docs/spm.md documents default dataset URIs "
        f"{sorted(uris)}, but the model ships {DEFAULT_DATASET!r}."
    )
    assert digests == {DEFAULT_DATASET_SHA256}, (
        f"docs/spm.md documents content hashes {sorted(digests)}, but "
        f"DEFAULT_DATASET_SHA256 is {DEFAULT_DATASET_SHA256!r}."
    )


def test_default_dataset_is_digested_once_per_resolved_file(monkeypatch, tmp_path):
    """The certified build is ~830 MB; construction must not re-digest it."""
    path = tmp_path / "counted.h5"
    path.write_bytes(b"populace")
    digests = []

    def counting_sha256(file_path):
        digests.append(str(file_path))
        return "0" * 64

    monkeypatch.setattr(system_module, "_file_sha256", counting_sha256)
    monkeypatch.setattr(system_module, "DEFAULT_DATASET_SHA256", "0" * 64)
    _verify_default_dataset(path)
    _verify_default_dataset(path)
    assert digests == [str(path)]
