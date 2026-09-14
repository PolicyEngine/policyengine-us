"""Construction and dataset contracts that require the Python simulation API."""

import hashlib
import json

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
from policyengine_us.spm import create_spm_provider, is_county_fips
from policyengine_us.system import DEFAULT_DATASET, _resolve_dataset_path, system


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

    correct = Simulation(
        tax_benefit_system=mistyped.tax_benefit_system,
        situation=single_person_situation(),
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
        **{
            entity: pd.DataFrame({f"{entity}_id": [1, 2]})
            for entity in groups
            if entity != "household"
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
    for name in FORMULA_OWNED_INPUTS:
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
