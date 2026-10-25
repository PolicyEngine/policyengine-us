"""Input compatibility, branch isolation and complete source round trips.

These cases cover Core's YAML builder as well as cloning, stored-input
bookkeeping and source export. They reuse the read-only country model and
tiny populations, without loading external data.
"""

import json
from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest
from policyengine_core.holders.helpers import (
    set_input_dispatch_by_period,
    set_input_divide_by_period,
)
from policyengine_core.periods import period
from policyengine_core.simulations import (
    Simulation as CoreSimulation,
    SimulationBuilder,
)

from policyengine_us import Microsimulation, Simulation
from policyengine_us.data.dataset_schema import USSingleYearDataset
from policyengine_us.data.economic_assumptions import (
    MICRODATA_UPRATING_OVERRIDES,
    extend_single_year_dataset,
)
from policyengine_us.system import system
from policyengine_us.tools.period_branch import drop_inherited_values
from policyengine_us.tools.social_security_inputs import (
    SOCIAL_SECURITY_COMPONENTS,
    export_source_inputs,
    reload_source_inputs,
)


class HouseholdMicrosimulation(Microsimulation):
    """Exercise the actual wrapper with a household instead of its default data."""

    default_dataset = None


WRAPPERS = (Simulation, HouseholdMicrosimulation)
FACTOR = "social_security_across_the_board_factor"


def situation(inputs):
    return {
        "people": {"person": {"age": {2024: 70, 2025: 71, 2026: 72}, **inputs}},
        "households": {"household": {"members": ["person"]}},
        "tax_units": {"tax_unit": {"members": ["person"]}},
        "spm_units": {"spm_unit": {"members": ["person"]}},
        "families": {"family": {"members": ["person"]}},
        "marital_units": {"marital_unit": {"members": ["person"]}},
    }


def make_simulation(wrapper=Simulation, inputs=None):
    return wrapper(situation=situation(inputs or {}), tax_benefit_system=system)


def make_core_simulation(inputs=None, route="dict_entities"):
    builder = SimulationBuilder()
    inputs = inputs or {}
    if route == "dict_entities":
        return builder.build_from_dict(system, situation(inputs))
    if route == "entities":
        return builder.build_from_entities(system, situation(inputs))
    variables = {
        "age": {2024: [70]},
        **{
            name: {period: [value] for period, value in values.items()}
            for name, values in inputs.items()
        },
    }
    if route == "dict_variables":
        return builder.build_from_dict(system, variables)
    return builder.build_from_variables(system, variables)


WRAPPER_WRITE_ROUTES = (
    *((wrapper, "simulation") for wrapper in WRAPPERS),
    (Simulation, "holder"),
)
CORE_WRITE_ROUTES = (
    *WRAPPER_WRITE_ROUTES,
    (make_core_simulation, "simulation"),
    (make_core_simulation, "dispatch"),
    (make_core_simulation, "divide"),
)


def write_public_input(simulation, name, input_period, values, route):
    if route in ("dispatch", "divide"):
        helper = (
            set_input_dispatch_by_period
            if route == "dispatch"
            else set_input_divide_by_period
        )
        return helper(
            simulation.get_holder(name), period(input_period), np.asarray(values)
        )
    if route == "holder":
        return simulation.get_holder(name).set_input(
            period=period(input_period),
            array=np.asarray(values),
            branch_name=simulation.branch_name,
        )
    return simulation.set_input(name, input_period, values)


def core_builder_wrapper(*, situation, tax_benefit_system):
    """Use raw Core with the same constructor shape as the public wrappers."""
    return SimulationBuilder().build_from_dict(tax_benefit_system, situation)


PERIOD_WRAPPERS = (*WRAPPERS, core_builder_wrapper)


def amount(simulation, name, period):
    return np.asarray(simulation.calculate(name, period))[0]


def input_periods(simulation, name):
    return {str(period) for period in simulation._get_set_input_periods(name)}


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_constructor_precedence_is_per_component_and_period(wrapper):
    inputs = {}
    for index, public in enumerate(SOCIAL_SECURITY_COMPONENTS, 1):
        inputs[public] = {2024: index * 1_000, 2026: index * 3_000}
        inputs[f"{public}_reported"] = {2025: index * 1_100, 2026: index * 1_200}
    simulation = make_simulation(wrapper, inputs)
    for year in (2024, 2025, 2026):
        simulation.set_input(FACTOR, year, [1.1])
    for index, public in enumerate(SOCIAL_SECURITY_COMPONENTS, 1):
        reported = f"{public}_reported"
        assert input_periods(simulation, public) == {"2026"}
        assert input_periods(simulation, reported) == {"2024", "2025", "2026"}
        assert amount(simulation, public, 2024) == pytest.approx(index * 1_100)
        assert amount(simulation, public, 2025) == pytest.approx(index * 1_210)
        assert amount(simulation, reported, 2026) == index * 1_200
        assert amount(simulation, public, 2026) == index * 3_000
        assert public in simulation.input_variables
        assert reported in simulation.input_variables


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_constructor_zero_and_aggregate_are_explicit_inputs(wrapper):
    inputs = {
        SOCIAL_SECURITY_COMPONENTS[0]: {2024: 0},
        f"{SOCIAL_SECURITY_COMPONENTS[1]}_reported": {2024: 0},
        SOCIAL_SECURITY_COMPONENTS[2]: {2024: 0},
        f"{SOCIAL_SECURITY_COMPONENTS[2]}_reported": {2024: 500},
        "social_security": {2024: 123},
    }
    simulation = make_simulation(wrapper, inputs)
    simulation.set_input(FACTOR, 2024, [1.5])
    for public in SOCIAL_SECURITY_COMPONENTS:
        assert amount(simulation, public, 2024) == 0
    assert amount(simulation, "social_security", 2024) == 123
    assert SOCIAL_SECURITY_COMPONENTS[0] not in simulation.input_variables
    assert f"{SOCIAL_SECURITY_COMPONENTS[0]}_reported" in simulation.input_variables


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_later_public_override_survives_clones_and_cache_clear(wrapper):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(wrapper, {public: {2024: 12_000}})
    assert amount(simulation, public, 2024) == 12_000
    simulation.set_input(public, 2024, [0])
    original_keys = set(simulation._user_input_keys)
    for copy in (
        simulation.clone(clone_tax_benefit_system=False),
        simulation.get_branch("override"),
    ):
        drop_inherited_values(copy)
        assert amount(copy, public, 2024) == 0
        copy.set_input(public, 2024, [42])
        drop_inherited_values(copy)
        assert amount(copy, public, 2024) == 42
        assert amount(copy, f"{public}_reported", 2024) == 42
        assert simulation._user_input_keys == original_keys
        assert amount(simulation, public, 2024) == 0
    assert amount(simulation, f"{public}_reported", 2024) == 0


@pytest.mark.parametrize(
    "route", ("dict_entities", "entities", "dict_variables", "variables")
)
def test_core_builder_migrates_initial_public_inputs_and_preserves_precedence(route):
    retirement, disability = SOCIAL_SECURITY_COMPONENTS[:2]
    simulation = make_core_simulation(
        {
            retirement: {2024: 12_000},
            disability: {2024: 777},
            f"{disability}_reported": {2024: 666},
            FACTOR: {2024: 1.1, 2026: 1.08},
        },
        route,
    )
    assert amount(simulation, retirement, 2024) == pytest.approx(13_200)
    assert input_periods(simulation, retirement) == set()
    assert input_periods(simulation, f"{retirement}_reported") == {"2024"}
    assert retirement not in simulation.input_variables
    assert f"{retirement}_reported" in simulation.input_variables
    later_source = amount(simulation, f"{retirement}_reported", 2026)
    assert later_source == pytest.approx(13_522.16, abs=0.01)
    assert amount(simulation, retirement, 2026) == pytest.approx(later_source * 1.08)
    # Existing both-name inputs retain the established explicit-override rule.
    assert amount(simulation, disability, 2024) == 777
    assert amount(simulation, f"{disability}_reported", 2024) == 666
    assert input_periods(simulation, disability) == {"2024"}
    assert disability in simulation.input_variables
    assert "age" in simulation.input_variables
    payload = simulation.extract_person(0)
    person = next(iter(payload["people"].values()))
    assert person[disability] == {"2024": 777}
    assert person[f"{disability}_reported"] == {"2024": 666}
    assert "age" in person
    simulation.set_input(retirement, 2024, [0])
    assert amount(simulation, retirement, 2024) == 0
    assert amount(simulation, f"{retirement}_reported", 2024) == 0
    simulation.set_input(disability, 2024, [42])
    assert amount(simulation, disability, 2024) == 42
    assert amount(simulation, f"{disability}_reported", 2024) == 666


@pytest.mark.parametrize("wrapper,write_route", CORE_WRITE_ROUTES)
@pytest.mark.parametrize("reported_input", (None, 0, 6_000))
def test_later_public_writes_refresh_automatic_sources_and_keep_explicit_twins(
    wrapper, write_route, reported_input
):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    inputs = {} if reported_input is None else {reported: {2024: reported_input}}
    simulation = (
        wrapper(inputs)
        if wrapper is make_core_simulation
        else make_simulation(wrapper, inputs)
    )
    # A calculated twin, even a cached zero, is not an explicitly supplied twin.
    assert amount(simulation, reported, 2024) == (reported_input or 0)
    simulation.set_input(FACTOR, 2024, [1.08])
    write_public_input(simulation, public, 2024, [12_000], write_route)
    expected_source = 12_000 if reported_input is None else reported_input
    assert amount(simulation, public, 2024) == 12_000
    assert amount(simulation, reported, 2024) == expected_source
    assert input_periods(simulation, reported) == {"2024"}
    assert public in simulation.input_variables
    assert reported in simulation.input_variables
    assert amount(simulation, public, 2026) == pytest.approx(
        expected_source * 13_522.16 / 12_000, abs=0.01
    )
    # Core's period-splitting helpers preserve an already supplied annual
    # input, and divide rejects a conflicting repeated total.
    replacement = 12_000 if write_route in ("dispatch", "divide") else 24_000
    write_public_input(simulation, public, 2024, [replacement], write_route)
    expected_source = replacement if reported_input is None else reported_input
    assert amount(simulation, reported, 2024) == expected_source
    drop_inherited_values(simulation)
    assert amount(simulation, public, 2026) == pytest.approx(
        expected_source * 13_522.16 / 12_000, abs=0.01
    )
    assert input_periods(simulation, reported) == {"2024"}


@pytest.mark.parametrize("wrapper", (*WRAPPERS, make_core_simulation))
def test_repeated_public_writes_refresh_migrated_sources_and_future_years(wrapper):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    inputs = {public: {2024: 12_000}}
    simulation = (
        wrapper(inputs)
        if wrapper is make_core_simulation
        else make_simulation(wrapper, inputs)
    )
    simulation.set_input(FACTOR, 2024, [1.08])
    simulation.set_input(FACTOR, 2026, [1.08])
    for override in (24_000, 18_000, 0):
        simulation.set_input(public, 2024, [override])
        drop_inherited_values(simulation)
        assert amount(simulation, public, 2024) == override
        assert amount(simulation, reported, 2024) == override
        assert amount(simulation, public, 2026) == pytest.approx(
            override * 13_522.16 / 12_000 * 1.08, abs=0.01
        )
        assert input_periods(simulation, public) == {"2024"}
    assert input_periods(simulation, reported) == {"2024"}


@pytest.mark.parametrize("explicit_source", (None, 0, 6_000))
def test_existing_builder_refreshes_loaded_sources_and_keeps_earlier_overrides(
    explicit_source,
):
    inputs = {name: {2024: 12_000} for name in SOCIAL_SECURITY_COMPONENTS}
    simulation = make_core_simulation(inputs)
    for name in SOCIAL_SECURITY_COMPONENTS:
        simulation.set_input(name, 2025, [18_000])
        if explicit_source is not None:
            simulation.set_input(f"{name}_reported", 2024, [explicit_source])
    SimulationBuilder().build_from_variables(
        system,
        {name: {2024: [24_000]} for name in SOCIAL_SECURITY_COMPONENTS},
        simulation=simulation,
    )
    for name in SOCIAL_SECURITY_COMPONENTS:
        assert amount(simulation, f"{name}_reported", 2024) == (
            24_000 if explicit_source is None else explicit_source
        )
        assert amount(simulation, name, 2025) == 18_000
        assert input_periods(simulation, name) == (
            {"2025"} if explicit_source is None else {"2024", "2025"}
        )


@pytest.mark.parametrize("route", ("builder", "dataset", "later"))
@pytest.mark.parametrize("explicit_source", (None, 0))
def test_failed_loading_synchronizes_successful_stores_without_changing_error(
    route, explicit_source
):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    failure = RuntimeError("setter failed after storing its input")

    class StoreThenRaise(CoreSimulation):
        fail_after_store = False

        def set_input(self, name, input_period, value):
            super().set_input(name, input_period, value)
            if self.fail_after_store and name == public:
                raise failure

    simulation = StoreThenRaise(situation=situation({}), tax_benefit_system=system)
    if explicit_source is not None:
        simulation.set_input(reported, 2024, [explicit_source])
    simulation.fail_after_store = True
    with pytest.raises(RuntimeError) as caught:
        if route == "builder":
            SimulationBuilder().build_from_variables(
                system, {public: {2024: [24_000]}}, simulation=simulation
            )
        elif route == "dataset":
            entities = ("household", "tax_unit", "spm_unit", "family", "marital_unit")
            frame = pd.DataFrame(
                {
                    "person_id": [1],
                    **{f"person_{entity}_id": [1] for entity in entities},
                    **{f"{entity}_id": [1] for entity in entities},
                    **(
                        {f"{reported}__2024": [explicit_source]}
                        if explicit_source is not None
                        else {}
                    ),
                    f"{public}__2024": [24_000],
                }
            )
            # Core accepts a DataFrame through its constructor, where it
            # resolves the dataset object before invoking this same loader.
            from policyengine_core.data import Dataset

            simulation.dataset = Dataset.from_dataframe(frame, time_period=2024)
            simulation.build_from_dataset()
        else:
            simulation.set_input(public, 2024, [24_000])
    assert caught.value is failure
    assert simulation._user_input_contexts == []
    assert amount(simulation, reported, 2024) == (
        24_000 if explicit_source is None else explicit_source
    )


@pytest.mark.parametrize("wrapper", (*WRAPPERS, make_core_simulation))
@pytest.mark.parametrize("explicit_source", (0, 12_000))
def test_direct_reported_holder_write_replaces_automatic_source_origin(
    wrapper, explicit_source
):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    inputs = {public: {2024: 12_000}}
    simulation = (
        wrapper(inputs)
        if wrapper is make_core_simulation
        else make_simulation(wrapper, inputs)
    )
    # A same-value write also becomes explicit; provenance cannot be inferred
    # by comparing the stored amount with its former automatic amount.
    simulation.get_holder(reported).set_input(
        2024, [explicit_source], simulation.branch_name
    )
    for override in (24_000, 18_000):
        simulation.set_input(public, 2024, [override])
        drop_inherited_values(simulation)
        assert amount(simulation, public, 2024) == override
        assert amount(simulation, reported, 2024) == explicit_source
        assert amount(simulation, public, 2026) == pytest.approx(
            explicit_source * 13_522.16 / 12_000, abs=0.01
        )


@pytest.mark.parametrize("wrapper", (*WRAPPERS, make_core_simulation))
def test_later_monthly_public_write_seeds_the_stored_rolling_year(wrapper):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = (
        wrapper() if wrapper is make_core_simulation else make_simulation(wrapper)
    )
    simulation.set_input(public, "2024-07", [12_000])
    # Core retains a rolling annual input for a monthly annual-flow write.
    assert input_periods(simulation, public) == {"year:2024-07"}
    assert input_periods(simulation, reported) == {"year:2024-07"}
    assert simulation.get_array(public, "year:2024-07")[0] == 12_000
    assert simulation.get_array(reported, "year:2024-07")[0] == 12_000
    # A monthly output reads the calendar year, whose January start precedes
    # the first rolling source in July. Main also returns zero here.
    assert amount(simulation, public, "2024-07") == 0
    assert amount(simulation, public, 2026) > 12_000


@pytest.mark.parametrize("wrapper,write_route", WRAPPER_WRITE_ROUTES)
def test_clone_and_branch_later_public_writes_keep_input_lists_private(
    wrapper, write_route
):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation(wrapper, {public: {2024: 12_000}})
    original_variables = list(simulation.input_variables)
    original_keys = set(simulation._user_input_keys)
    parent_later_source = amount(simulation, reported, 2025)
    for copy in (
        simulation.clone(clone_tax_benefit_system=False),
        simulation.get_branch("new_public_override"),
    ):
        write_public_input(copy, public, 2025, [24_000], write_route)
        drop_inherited_values(copy)
        assert amount(copy, public, 2025) == 24_000
        assert amount(copy, reported, 2025) == 24_000
        assert amount(copy, public, 2026) > 24_000
        assert public in copy.input_variables
        assert copy.input_variables is not simulation.input_variables
        assert simulation.input_variables == original_variables
        assert simulation._user_input_keys == original_keys
        assert amount(simulation, public, 2025) == parent_later_source
        assert input_periods(simulation, reported) == {"2024"}


def test_holder_write_before_branch_creation_stays_in_its_named_branch():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation()
    simulation.get_holder(public).set_input(
        period=period(2024), array=np.array([12_000]), branch_name="later"
    )
    branch = simulation.get_branch("later")
    assert amount(branch, public, 2024) == 12_000
    assert amount(branch, reported, 2024) == 12_000
    assert amount(branch, public, 2026) == pytest.approx(13_522.16, abs=0.01)
    for year in (2024, 2026):
        assert amount(simulation, public, year) == 0
        assert amount(simulation, reported, year) == 0

    reloaded = Simulation(situation=branch.extract_person(0), tax_benefit_system=system)
    assert amount(reloaded, public, 2024) == 12_000
    assert amount(reloaded, public, 2026) == pytest.approx(13_522.16, abs=0.01)
    clone = branch.clone(clone_tax_benefit_system=False)
    write_public_input(clone, public, 2024, [24_000], "holder")
    drop_inherited_values(clone)
    assert amount(clone, public, 2026) == pytest.approx(27_044.32, abs=0.01)
    assert amount(branch, public, 2026) == pytest.approx(13_522.16, abs=0.01)
    assert amount(reloaded, public, 2026) == pytest.approx(13_522.16, abs=0.01)
    assert amount(simulation, public, 2026) == 0


@pytest.mark.parametrize("is_input", (None, True))
def test_context_stores_synchronize_sources_in_the_effective_branch(is_input):
    retirement, disability = SOCIAL_SECURITY_COMPONENTS[:2]
    simulation = make_simulation(inputs={f"{disability}_reported": {2024: 0}})
    # Core restoration and custom input handlers use _set directly. Its
    # default branch follows the active input context, including a branch
    # that has no simulation object yet.
    simulation._user_input_contexts.append("context_inputs")
    try:
        for public in (retirement, disability):
            simulation.get_holder(public)._set(
                period(2024), np.array([12_000]), is_input=is_input
            )
    finally:
        simulation._user_input_contexts.pop()

    branch = simulation.get_branch("context_inputs")
    for public in (retirement, disability):
        assert amount(branch, public, 2024) == 12_000
        assert amount(simulation, public, 2024) == 0
        assert (public, "context_inputs", period(2024)) in branch._user_input_keys
    assert amount(branch, f"{retirement}_reported", 2024) == 12_000
    # An inherited explicit zero keeps precedence over a public input.
    assert amount(branch, f"{disability}_reported", 2024) == 0
    for public in (retirement, disability):
        branch.set_input(public, 2024, [24_000])
    drop_inherited_values(branch)
    assert amount(branch, f"{retirement}_reported", 2024) == 24_000
    assert amount(branch, retirement, 2026) == pytest.approx(27_044.32, abs=0.01)
    assert amount(branch, f"{disability}_reported", 2024) == 0
    assert amount(branch, disability, 2026) == 0
    assert amount(simulation, f"{retirement}_reported", 2024) == 0


def test_explicit_noninput_store_keeps_its_branch_inside_an_input_context():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation()
    simulation._user_input_contexts.append("context_inputs")
    try:
        simulation.get_holder(public)._set(
            period(2024), np.array([12_000]), is_input=False
        )
    finally:
        simulation._user_input_contexts.pop()
    for name in (public, reported):
        assert set(simulation.get_holder(name).get_known_branch_periods()) == {
            ("default", period(2024))
        }
        assert input_periods(simulation, name) == set()
        assert amount(simulation, name, 2024) == 12_000
    assert amount(simulation, public, 2026) == pytest.approx(13_522.16, abs=0.01)


def test_failing_period_handler_synchronizes_the_inputs_it_already_stored(monkeypatch):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation()
    branch = simulation.get_branch("partial_handler")

    def store_then_fail(holder, requested_period, array):
        holder._set(requested_period.this_year, array)
        raise RuntimeError("handler failed after storing its annual input")

    monkeypatch.setattr(system.variables[public], "set_input", store_then_fail)
    with pytest.raises(RuntimeError, match="after storing"):
        branch.get_holder(public).set_input(
            period("2024-07"), np.array([12_000]), branch.branch_name
        )
    assert branch._user_input_contexts == []
    assert amount(branch, public, 2024) == 12_000
    assert amount(branch, reported, 2024) == 12_000
    assert input_periods(branch, reported) == {"2024"}
    assert amount(branch, public, 2026) == pytest.approx(13_522.16, abs=0.01)
    branch.set_input(public, 2024, [24_000])
    drop_inherited_values(branch)
    assert amount(branch, reported, 2024) == 24_000
    assert amount(branch, public, 2026) == pytest.approx(27_044.32, abs=0.01)
    assert amount(simulation, public, 2024) == 0
    assert amount(simulation, reported, 2024) == 0


@pytest.mark.parametrize("route", ("store_default", "store_noninput", "cache"))
def test_raw_nonderived_stores_keep_carry_sources_without_becoming_inputs(route):
    retirement, disability = SOCIAL_SECURITY_COMPONENTS[:2]
    simulation = make_simulation(inputs={f"{disability}_reported": {2024: 0}})
    for public in (retirement, disability):
        holder = simulation.get_holder(public)
        if route == "cache":
            holder.put_in_cache(np.array([12_000]), period(2024), derived=False)
        else:
            holder._set(
                period(2024),
                np.array([12_000]),
                is_input=False if route == "store_noninput" else None,
            )
        assert amount(simulation, public, 2024) == 12_000
        assert input_periods(simulation, public) == set()
        assert public not in simulation.input_variables
    assert amount(simulation, f"{retirement}_reported", 2024) == 12_000
    assert input_periods(simulation, f"{retirement}_reported") == set()
    assert f"{retirement}_reported" not in simulation.input_variables
    assert amount(simulation, retirement, 2026) == pytest.approx(13_522.16, abs=0.01)
    assert amount(simulation, f"{disability}_reported", 2024) == 0
    assert amount(simulation, disability, 2026) == 0
    # A later replayable input replaces its automatic cache source and still
    # respects a separately supplied reported source.
    for public in (retirement, disability):
        simulation.set_input(public, 2024, [24_000])
    drop_inherited_values(simulation)
    assert amount(simulation, f"{retirement}_reported", 2024) == 24_000
    assert input_periods(simulation, f"{retirement}_reported") == {"2024"}
    assert amount(simulation, retirement, 2026) == pytest.approx(27_044.32, abs=0.01)
    assert amount(simulation, f"{disability}_reported", 2024) == 0
    assert amount(simulation, disability, 2026) == 0


@pytest.mark.parametrize("route", ("cache", "store_noninput"))
@pytest.mark.parametrize("ingress", ("builder", "situation", "dataset"))
def test_initial_raw_handler_stores_keep_sources_and_explicit_twin_priority(
    monkeypatch, route, ingress
):
    retirement, disability = SOCIAL_SECURITY_COMPONENTS[:2]

    def store_raw_source(holder, requested_period, array):
        if route == "cache":
            holder.put_in_cache(array, requested_period.this_year)
        else:
            holder._set(requested_period.this_year, array, is_input=False)

    for public in (retirement, disability):
        monkeypatch.setattr(system.variables[public], "set_input", store_raw_source)
    inputs = {
        retirement: {"2024-07": 12_000},
        f"{disability}_reported": {2024: 0},
        disability: {"2024-07": 12_000},
    }
    if ingress == "builder":
        simulation = make_core_simulation(inputs, route="entities")
    elif ingress == "situation":
        simulation = CoreSimulation(
            situation=situation(inputs), tax_benefit_system=system
        )
    else:
        entities = ("household", "tax_unit", "spm_unit", "family", "marital_unit")
        frame = pd.DataFrame(
            {
                "person_id": [1],
                **{f"person_{entity}_id": [1] for entity in entities},
                **{f"{entity}_id": [1] for entity in entities},
                **{
                    f"{name}__{input_period}": [value]
                    for name, values in inputs.items()
                    for input_period, value in values.items()
                },
            }
        )
        simulation = CoreSimulation(
            dataset=frame,
            tax_benefit_system=system,
            default_input_period=2024,
            default_calculation_period=2024,
        )
    for public in (retirement, disability):
        assert amount(simulation, public, 2024) == 12_000
        assert input_periods(simulation, public) == set()
    assert amount(simulation, f"{retirement}_reported", 2024) == 12_000
    assert input_periods(simulation, f"{retirement}_reported") == set()
    assert amount(simulation, retirement, 2026) == pytest.approx(13_522.16, abs=0.01)
    assert amount(simulation, f"{disability}_reported", 2024) == 0
    assert input_periods(simulation, f"{disability}_reported") == {"2024"}
    assert amount(simulation, disability, 2026) == 0


def test_raw_memory_mirror_keeps_a_surviving_disk_source_automatic(tmp_path):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation()
    reported_holder = simulation.get_holder(reported)
    reported_holder._disk_storage = reported_holder.create_disk_storage(
        tmp_path, preserve=True
    )
    reported_holder._on_disk_storable = True
    simulation.memory_config = SimpleNamespace(
        max_memory_occupation_pc=0,
        priority_variables=system.variables,
        variables_to_drop=(),
    )
    stored_period = period(2024)
    simulation.set_input(public, 2024, [12_000])
    assert reported_holder._memory_storage.get(stored_period) is None
    np.testing.assert_array_equal(
        reported_holder._disk_storage.get(stored_period), [12_000]
    )

    # A raw memory cache shadows the disk input without replacing its
    # replayable tier or erasing that tier's automatic-source provenance.
    reported_holder._on_disk_storable = False
    simulation.get_holder(public).put_in_cache(np.array([18_000]), stored_period)
    np.testing.assert_array_equal(
        reported_holder._memory_storage.get(stored_period), [18_000]
    )
    np.testing.assert_array_equal(
        simulation._get_recorded_input_array(reported, stored_period), [12_000]
    )
    simulation._invalidate_all_caches()
    assert reported_holder._memory_storage.get(stored_period) is None
    np.testing.assert_array_equal(
        reported_holder._disk_storage.get(stored_period), [12_000]
    )
    reported_holder._on_disk_storable = True
    simulation.set_input(public, 2024, [24_000])
    np.testing.assert_array_equal(
        reported_holder._disk_storage.get(stored_period), [24_000]
    )
    assert amount(simulation, reported, 2024) == 24_000
    assert amount(simulation, public, 2026) == pytest.approx(27_044.32, abs=0.01)


def test_derived_public_caches_never_become_reported_carry_sources():
    retirement, disability = SOCIAL_SECURITY_COMPONENTS[:2]
    simulation = make_simulation()
    # A calculation can cache through either API, even within an input
    # handler. Core explicitly excludes derived stores from input contexts.
    simulation._user_input_contexts.append(simulation.branch_name)
    try:
        simulation.get_holder(retirement)._set(
            period(2024), np.array([12_000]), derived=True
        )
        simulation.get_holder(disability).put_in_cache(
            np.array([12_000]), period(2024), derived=True
        )
    finally:
        simulation._user_input_contexts.pop()
    for public in (retirement, disability):
        assert amount(simulation, public, 2024) == 12_000
        assert input_periods(simulation, public) == set()
        assert simulation.get_array(f"{public}_reported", 2024) is None
        assert input_periods(simulation, f"{public}_reported") == set()
        assert amount(simulation, public, 2026) == 0


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_branch_explicit_twin_overrides_inherited_automatic_source_privately(wrapper):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation(wrapper, {public: {2024: 12_000}})
    explicit = simulation.get_branch("explicit_reported_source")
    explicit.set_input(reported, 2024, [0])
    automatic = simulation.get_branch("inherited_automatic_source")
    for copy in (explicit, automatic):
        copy.set_input(public, 2024, [24_000])
        drop_inherited_values(copy)
        assert amount(copy, public, 2024) == 24_000
    assert amount(explicit, reported, 2024) == 0
    assert amount(explicit, public, 2026) == 0
    assert amount(automatic, reported, 2024) == 24_000
    assert amount(automatic, public, 2026) == pytest.approx(27_044.32, abs=0.01)
    assert amount(simulation, reported, 2024) == 12_000
    # A branch's explicit replacement must not mark its parent's automatic
    # source explicit, or prevent the parent's next public write from seeding.
    simulation.set_input(public, 2024, [36_000])
    assert amount(simulation, reported, 2024) == 36_000
    assert amount(explicit, reported, 2024) == 0
    assert amount(automatic, reported, 2024) == 24_000


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_neutral_reform_replay_keeps_automatic_source_origin_private(wrapper):
    from policyengine_core.reforms import Reform

    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation(wrapper, {public: {2024: 12_000}})
    parent_later = amount(simulation, public, 2026)
    branch = simulation.get_branch("replayed_automatic_source", clone_system=True)
    branch.apply_reform(
        Reform.from_dict(
            {"gov.contrib.ssa.benefit_levers.across_the_board.rate": {"2024": 0}}
        )
    )
    branch.set_input(public, 2024, [24_000])
    assert amount(branch, reported, 2024) == 24_000
    assert amount(branch, public, 2024) == 24_000
    assert amount(branch, public, 2026) == pytest.approx(27_044.32, abs=0.01)
    assert input_periods(branch, reported) == {"2024"}
    assert amount(simulation, reported, 2024) == 12_000
    assert amount(simulation, public, 2026) == parent_later


@pytest.mark.parametrize(
    "wrapper,factor", ((Microsimulation, 1.1), (CoreSimulation, 1.08))
)
def test_dataset_constructor_migrates_stored_original_columns(wrapper, factor):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    frame = pd.DataFrame(
        {
            "person_id": [1],
            **{
                f"person_{entity}_id": [1]
                for entity in (
                    "household",
                    "tax_unit",
                    "spm_unit",
                    "family",
                    "marital_unit",
                )
            },
            **{
                f"{entity}_id": [1]
                for entity in (
                    "household",
                    "tax_unit",
                    "spm_unit",
                    "family",
                    "marital_unit",
                )
            },
            f"{public}__2024": [12_000],
            f"{public}__2026": [14_000],
            f"{public}_reported__2026": [13_000],
        }
    )
    simulation = wrapper(
        dataset=frame,
        tax_benefit_system=system,
        default_input_period=2024,
        default_calculation_period=2024,
    )
    simulation.set_input(FACTOR, 2024, [factor])
    simulation.set_input(FACTOR, 2026, [factor])
    assert amount(simulation, public, 2024) == pytest.approx(12_000 * factor)
    assert amount(simulation, public, 2026) == 14_000
    assert amount(simulation, f"{public}_reported", 2026) == 13_000
    assert input_periods(simulation, public) == {"2026"}
    assert input_periods(simulation, f"{public}_reported") == {"2024", "2026"}
    # Loader-time public writes migrate; later writes remain final outputs.
    simulation.set_input(public, 2024, [0])
    assert amount(simulation, public, 2024) == 0
    assert amount(simulation, f"{public}_reported", 2024) == 0
    reloaded = reload_source_inputs(
        export_source_inputs(simulation), tax_benefit_system=system
    )
    assert amount(reloaded, public, 2024) == 0
    assert amount(reloaded, f"{public}_reported", 2024) == 0


def test_complete_snapshot_preserves_histories_and_separate_final_overrides():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(
        inputs={
            f"{public}_reported": {2024: 12_000, 2026: 14_000},
            public: {2026: 6_500},
            f"{public}_source": {2024: "reported", 2026: "reported"},
            "ss_aime_input": {2024: 1_000, 2026: 2_000},
            "employment_income": {2024: 10_000, 2026: 20_000},
        }
    )
    # A calculated intervening year must never become a reported source.
    amount(simulation, public, 2025)
    simulation.set_input(public, 2027, [0])
    payload = json.loads(json.dumps(export_source_inputs(simulation)))
    person = payload["sources"]["people"]["person"]
    assert set(person[f"{public}_reported"]) == {"2024", "2026", "2027"}
    assert public not in person
    assert set(payload["overrides"][public]) == {"2026", "2027"}
    assert person["ss_aime_input"] == {"2024": 1_000, "2026": 2_000}
    reloaded = reload_source_inputs(payload, tax_benefit_system=system)
    for name in (public, f"{public}_reported", "ss_aime_input", "employment_income"):
        for year in (2024, 2025, 2026, 2027):
            assert amount(reloaded, name, year) == pytest.approx(
                amount(simulation, name, year)
            )
    assert input_periods(reloaded, public) == {"2026", "2027"}
    assert export_source_inputs(reloaded)["overrides"][public]["2027"] == [0]
    reloaded.set_input(public, 2027, [24_000])
    assert amount(reloaded, f"{public}_reported", 2027) == 24_000
    assert amount(reloaded, public, 2028) > 24_000
    assert amount(simulation, f"{public}_reported", 2027) == 0


def test_legacy_extraction_uses_reported_sources_and_months_keep_flow_conversion():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(HouseholdMicrosimulation, {public: {2024: 12_000}})
    extracted = simulation.extract_person(0)
    person = next(iter(extracted["people"].values()))
    assert f"{public}_reported" in person
    assert public not in person
    reloaded = Simulation(situation=extracted, tax_benefit_system=system)
    for month_first in (False, True):
        copy = reloaded.clone(clone_tax_benefit_system=False)
        if month_first:
            assert amount(copy, public, "2024-07") == 1_000
        assert amount(copy, public, 2024) == 12_000
        assert amount(copy, public, "2024-07") == 1_000
    reloaded.set_input(public, 2024, [24_000])
    assert amount(reloaded, f"{public}_reported", 2024) == 24_000
    assert amount(reloaded, public, 2026) == pytest.approx(27_044.32, abs=0.01)


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize("override", (0, 24_000))
def test_legacy_extraction_preserves_later_public_override(wrapper, override):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation(wrapper, {public: {2024: 12_000}})
    simulation.set_input(public, 2024, [override])
    extracted = simulation.extract_person(0)
    person = next(iter(extracted["people"].values()))
    assert person[public]["2024"] == override
    assert person[reported]["2024"] == override
    reloaded = Simulation(situation=extracted, tax_benefit_system=system)
    assert amount(reloaded, public, 2024) == override
    assert amount(reloaded, reported, 2024) == override


@pytest.mark.parametrize("wrapper", WRAPPERS)
@pytest.mark.parametrize("explicit_source", (None, 0, 6_000))
def test_legacy_extraction_keeps_later_override_and_matching_source(
    wrapper, explicit_source
):
    from policyengine_core.reforms import Reform

    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    inputs = situation({public: {2024: 1_000}})
    inputs["people"]["other"] = {"age": {2024: 70}, public: {2024: 12_000}}
    for plural, groups in inputs.items():
        if plural != "people":
            groups["other"] = {"members": ["other"]}
    reform = Reform.from_dict(
        {
            "gov.contrib.ssa.benefit_levers.across_the_board.start_year": {
                "2026": 2026
            },
            "gov.contrib.ssa.benefit_levers.across_the_board.rate": {"2026": 0.08},
        }
    )
    simulation = wrapper(situation=inputs, tax_benefit_system=system, reform=reform)
    # Core's first known public period is now a calculated 2024 cache, so it
    # cannot identify the later supplied override without recorded-input APIs.
    np.testing.assert_array_equal(simulation.calculate(public, 2024), [1_000, 12_000])
    if explicit_source is not None:
        simulation.set_input(reported, 2026, [500, explicit_source])
    simulation.set_input(public, 2026, [18_000, 24_000])
    expected_source = 24_000 if explicit_source is None else explicit_source

    # Select the second household: its Core extraction label retains index 2,
    # while its reloaded population contains just one person at index 0.
    payload = simulation.extract_person(1)
    assert set(payload["people"]) == {"person_2"}
    person = payload["people"]["person_2"]
    assert person[public] == {"2026": 24_000}
    assert person[reported] == {"2024": 12_000, "2026": expected_source}
    reloaded = Simulation(situation=payload, tax_benefit_system=system, reform=reform)
    assert input_periods(reloaded, public) == {"2026"}
    # Reload must retain the final override, despite the 1.08 benefit factor.
    assert amount(reloaded, public, 2026) == 24_000
    assert amount(reloaded, reported, 2026) == expected_source
    assert amount(reloaded, public, 2027) == pytest.approx(
        np.asarray(simulation.calculate(public, 2027))[1]
    )

    reloaded.set_input(public, 2026, [36_000])
    assert amount(reloaded, reported, 2026) == (
        36_000 if explicit_source is None else explicit_source
    )
    assert np.asarray(simulation.calculate(reported, 2026))[1] == expected_source
    simulation.set_input(public, 2026, [18_000, 36_000])
    for candidate in (simulation, reloaded):
        drop_inherited_values(candidate)
    assert amount(reloaded, public, 2026) == 36_000
    assert amount(reloaded, public, 2027) == pytest.approx(
        np.asarray(simulation.calculate(public, 2027))[1]
    )


@pytest.mark.parametrize("wrapper,write_route", WRAPPER_WRITE_ROUTES)
@pytest.mark.parametrize("snapshot", ("legacy_extraction", "complete_export"))
def test_source_round_trip_retains_automatic_origin_for_subsequent_writes(
    wrapper, write_route, snapshot
):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation(wrapper, {public: {2024: 12_000}})
    write_public_input(simulation, public, 2024, [24_000], write_route)
    # A cached intervening source is not exported or treated as supplied.
    amount(simulation, reported, 2025)
    if snapshot == "legacy_extraction":
        payload = json.loads(json.dumps(simulation.extract_person(0)))
        person = next(iter(payload["people"].values()))
        reloaded = Simulation(situation=payload, tax_benefit_system=system)
        assert person[public] == {"2024": 24_000}
    else:
        payload = json.loads(json.dumps(export_source_inputs(simulation)))
        person = next(iter(payload["sources"]["people"].values()))
        reloaded = reload_source_inputs(payload, tax_benefit_system=system)
        assert public not in person
        assert payload["overrides"][public] == {"2024": [24_000]}
    assert person[reported] == {"2024": 24_000}
    assert set(person).issubset(system.variables)
    write_public_input(reloaded, public, 2024, [36_000], write_route)
    assert amount(reloaded, public, 2024) == 36_000
    assert amount(reloaded, reported, 2024) == 36_000
    assert amount(reloaded, public, 2026) == pytest.approx(40_566.48, abs=0.02)
    assert input_periods(reloaded, reported) == {"2024"}
    assert amount(simulation, reported, 2024) == 24_000


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_complete_reload_reform_baseline_retains_automatic_source_origin(wrapper):
    from policyengine_core.reforms import Reform

    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation(wrapper, {public: {2024: 12_000}})
    simulation.set_input(public, 2024, [24_000])
    reloaded = reload_source_inputs(
        export_source_inputs(simulation),
        tax_benefit_system=system,
        reform=Reform.from_dict(
            {"gov.contrib.ssa.benefit_levers.across_the_board.rate": {"2024": 0}}
        ),
    )
    baseline = reloaded.baseline
    assert baseline is not None
    baseline.set_input(public, 2024, [36_000])
    assert amount(baseline, public, 2024) == 36_000
    assert amount(baseline, reported, 2024) == 36_000
    assert amount(baseline, public, 2026) == pytest.approx(40_566.48, abs=0.02)
    assert amount(reloaded, reported, 2024) == 24_000
    reloaded.set_input(public, 2024, [48_000])
    assert amount(reloaded, reported, 2024) == 48_000
    assert amount(reloaded, public, 2026) == pytest.approx(54_088.64, abs=0.02)
    assert amount(baseline, reported, 2024) == 36_000
    assert amount(simulation, reported, 2024) == 24_000


@pytest.mark.parametrize("wrapper", WRAPPERS)
def test_explicit_only_legacy_extraction_needs_no_provenance_envelope(wrapper):
    retirement, disability = SOCIAL_SECURITY_COMPONENTS[:2]
    simulation = make_simulation(
        wrapper,
        {
            f"{retirement}_reported": {2024: 0},
            f"{disability}_reported": {2024: 6_000},
        },
    )
    payload = simulation.extract_person(0)
    assert set(payload).issubset(system.entities_plural())
    person = next(iter(payload["people"].values()))
    assert set(person).issubset(system.variables)
    reloaded = Simulation(situation=payload, tax_benefit_system=system)
    reloaded.set_input(retirement, 2024, [24_000])
    reloaded.set_input(disability, 2024, [12_000])
    assert amount(reloaded, f"{retirement}_reported", 2024) == 0
    assert amount(reloaded, f"{disability}_reported", 2024) == 6_000
    assert amount(reloaded, retirement, 2026) == 0
    assert amount(reloaded, disability, 2026) == pytest.approx(6_761.08, abs=0.01)


def test_reported_twins_are_pure_and_original_dataset_names_keep_their_uprater():
    for public in SOCIAL_SECURITY_COMPONENTS:
        original = system.get_variable(public)
        reported = system.get_variable(f"{public}_reported")
        assert not original.is_input_variable()
        assert original.uprating is None
        assert reported.is_input_variable()
        assert reported.label == original.label
        assert not reported.formulas and not reported.adds and not reported.subtracts
        assert reported.uprating.endswith("social_security_per_capita")
        assert (
            MICRODATA_UPRATING_OVERRIDES[public]
            == "calibration.gov.irs.soi.social_security"
        )


@pytest.mark.parametrize(
    "source", ["supplied_aime", "supplied_pia", "supplied_ratio_survivor", "history"]
)
def test_reserved_sources_fail_explicitly_instead_of_using_reported_fallback(source):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(
        inputs={f"{public}_source": {2024: source}, f"{public}_reported": {2024: 0}}
    )
    with pytest.raises(NotImplementedError, match="reserved"):
        simulation.calculate(public, 2024)


def test_oasi_only_cut_rejects_unidentified_positive_dependent_stream():
    from policyengine_core.reforms import Reform

    reform = Reform.from_dict(
        {
            "gov.contrib.ssa.benefit_levers.payable.share": {"2024": 0.8},
            "gov.contrib.ssa.benefit_levers.payable.oasi_only": {"2024": True},
        }
    )
    simulation = Simulation(
        situation=situation({"social_security_dependents_reported": {2024: 500}}),
        reform=reform,
        tax_benefit_system=system,
    )
    with pytest.raises(ValueError, match="dependent benefit fund"):
        simulation.calculate("social_security_dependents", 2024)


def test_parameter_reform_registration_order_preserves_stable_public_formula():
    from policyengine_core.reforms import Reform

    across = Reform.from_dict(
        {
            "gov.contrib.ssa.benefit_levers.across_the_board.start_year": {
                "2024": 2024
            },
            "gov.contrib.ssa.benefit_levers.across_the_board.rate": {"2024": 0.1},
        }
    )
    payable = Reform.from_dict(
        {"gov.contrib.ssa.benefit_levers.payable.share": {"2024": 0.8}}
    )
    first = Simulation(
        situation=situation({"social_security_retirement_reported": {2024: 12000}}),
        reform=(across, payable),
        tax_benefit_system=system,
    )
    second = Simulation(
        situation=situation({"social_security_retirement_reported": {2024: 12000}}),
        reform=(payable, across),
        tax_benefit_system=system,
    )
    assert amount(first, "social_security_retirement", 2024) == pytest.approx(10560)
    assert amount(second, "social_security_retirement", 2024) == pytest.approx(10560)
    assert (
        first.tax_benefit_system.variables["social_security_retirement"].formulas
        == second.tax_benefit_system.variables["social_security_retirement"].formulas
    )


@pytest.mark.parametrize("wrapper", PERIOD_WRAPPERS)
def test_exact_multi_year_sources_keep_keys_uniform_factors_and_overrides(wrapper):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    multi_year = "year:2024:2"
    simulation = make_simulation(wrapper, {public: {multi_year: 24_000}})
    # Core's weighted Microsimulation API needs a weight for this exact
    # noncanonical request, just as it does for an exact public input on main.
    simulation.set_input("household_weight", multi_year, [1])
    assert input_periods(simulation, public) == set()
    assert input_periods(simulation, reported) == {multi_year}
    assert amount(simulation, public, multi_year) == 24_000
    parent_keys = set(simulation._user_input_keys)
    uniform = simulation.get_branch("uniform_multi_year")
    for year in (2024, 2025):
        uniform.set_input(FACTOR, year, [1.1])
    drop_inherited_values(uniform)
    assert amount(uniform, public, multi_year) == pytest.approx(26_400)
    assert simulation._user_input_keys == parent_keys
    assert amount(simulation, public, multi_year) == 24_000
    reloaded = reload_source_inputs(
        export_source_inputs(uniform), tax_benefit_system=system
    )
    assert input_periods(reloaded, reported) == {multi_year}
    assert input_periods(reloaded, "household_weight") == {multi_year}
    assert amount(reloaded, public, multi_year) == pytest.approx(26_400)
    uniform.set_input(public, multi_year, [0])
    clone = uniform.clone(clone_tax_benefit_system=False)
    drop_inherited_values(clone)
    assert input_periods(clone, "household_weight") == {multi_year}
    assert amount(clone, public, multi_year) == 0
    override_reload = reload_source_inputs(
        export_source_inputs(clone), tax_benefit_system=system
    )
    assert amount(override_reload, public, multi_year) == 0
    assert amount(override_reload, reported, multi_year) == 0
    assert input_periods(override_reload, "household_weight") == {multi_year}


@pytest.mark.parametrize("wrapper", PERIOD_WRAPPERS)
def test_exact_multi_year_both_names_and_neutralization_keep_core_precedence(
    monkeypatch, wrapper
):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    multi_year = "year:2024:2"
    simulation = make_simulation(
        wrapper, {public: {multi_year: 123}, reported: {multi_year: 24_000}}
    )
    simulation.set_input("household_weight", multi_year, [1])
    simulation.set_input(FACTOR, 2024, [1.1])
    simulation.set_input(FACTOR, 2025, [0.8])
    assert amount(simulation, public, multi_year) == 123
    assert amount(simulation, reported, multi_year) == 24_000
    neutralized = make_simulation(wrapper, {reported: {multi_year: 24_000}})
    neutralized.set_input("household_weight", multi_year, [1])
    with monkeypatch.context() as context:
        context.setattr(system.variables[public], "is_neutralized", True)
        assert amount(neutralized, public, multi_year) == 0


@pytest.mark.parametrize("wrapper", PERIOD_WRAPPERS)
@pytest.mark.parametrize(
    "multi_year,annual_factors",
    (
        ("year:2024:2", {2024: 1.1, 2025: 0.8}),
        ("year:2024-07:2", {2024: 1.1, 2025: 1.1, 2026: 0.8}),
    ),
)
def test_exact_multi_year_source_rejects_differing_annual_factors_without_allocation(
    wrapper, multi_year, annual_factors
):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(wrapper, {public: {multi_year: 24_000}})
    simulation.set_input("household_weight", multi_year, [1])
    assert amount(simulation, public, multi_year) == 24_000
    for year, factor in annual_factors.items():
        simulation.set_input(FACTOR, year, [factor])
    drop_inherited_values(simulation)
    with pytest.raises(ValueError, match="separately supplied annual source amounts"):
        simulation.calculate(public, multi_year)
    assert input_periods(simulation, f"{public}_reported") == {multi_year}


def test_containing_period_migration_preserves_sources_and_inner_final_overrides():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    simulation = make_simulation(
        inputs={
            public: {2024: 123, "year:2024:10": 100_000, "year:2024:2": 24_000},
            reported: {2024: 12_000},
        }
    )
    assert input_periods(simulation, public) == {"2024"}
    assert input_periods(simulation, reported) == {
        "2024",
        "year:2024:2",
        "year:2024:10",
    }
    assert amount(simulation, public, 2024) == 123
    assert amount(simulation, reported, 2024) == 12_000
    assert amount(simulation, public, "year:2024:2") == 24_000
    assert amount(simulation, reported, "year:2024:10") == 100_000


@pytest.mark.parametrize("wrapper", PERIOD_WRAPPERS)
def test_multi_year_selected_base_input_and_neutralization_take_precedence(
    monkeypatch, wrapper
):
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported, base = f"{public}_reported", f"{public}_base"
    multi_year = "year:2024:2"
    simulation = make_simulation(
        wrapper, {reported: {multi_year: 24_000}, base: {multi_year: 6_000}}
    )
    simulation.set_input("household_weight", multi_year, [1])
    for year in (2024, 2025):
        simulation.set_input(FACTOR, year, [1.1])
    assert amount(simulation, public, multi_year) == pytest.approx(6_600)
    reloaded = reload_source_inputs(
        export_source_inputs(simulation), tax_benefit_system=system
    )
    assert amount(reloaded, public, multi_year) == pytest.approx(6_600)

    base_only = make_simulation(wrapper, {base: {multi_year: 6_000}})
    base_only.set_input("household_weight", multi_year, [1])
    assert amount(base_only, public, multi_year) == 6_000
    neutralized = make_simulation(
        wrapper, {reported: {multi_year: 24_000}, base: {multi_year: 6_000}}
    )
    neutralized.set_input("household_weight", multi_year, [1])
    neutralized.set_input(FACTOR, 2024, [1.1])
    neutralized.set_input(FACTOR, 2025, [0.8])
    with monkeypatch.context() as context:
        context.setattr(system.variables[base], "is_neutralized", True)
        assert amount(neutralized, public, multi_year) == 0


def test_multi_year_reported_total_rejects_partial_base_overrides():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    simulation = make_simulation(
        inputs={
            f"{public}_reported": {"year:2024:2": 24_000},
            f"{public}_base": {2024: 6_000},
        }
    )
    with pytest.raises(ValueError, match="base overrides for other periods"):
        simulation.calculate(public, "year:2024:2")


def test_multi_year_zero_rows_do_not_require_annual_allocation():
    public = SOCIAL_SECURITY_COMPONENTS[0]
    reported = f"{public}_reported"
    multi_year = "year:2024:2"
    inputs = {
        "people": {
            "positive": {reported: {multi_year: 24_000}},
            "zero": {reported: {multi_year: 0}},
        },
        "households": {"household": {"members": ["positive", "zero"]}},
    }
    simulation = Simulation(situation=inputs, tax_benefit_system=system)
    simulation.set_input(FACTOR, 2024, [1.1, 1.1])
    simulation.set_input(FACTOR, 2025, [1.1, 0.8])
    np.testing.assert_allclose(simulation.calculate(public, multi_year), [26_400, 0])
    all_zero = simulation.get_branch("all_zero_multi_year")
    all_zero.set_input(reported, multi_year, [0, 0])
    drop_inherited_values(all_zero)
    np.testing.assert_array_equal(all_zero.calculate(public, multi_year), [0, 0])


def test_dimensionless_benefit_factors_keep_annual_levels_on_monthly_requests():
    factor_names = (
        "social_security_across_the_board_factor",
        "social_security_payable_factor",
        *(
            f"{component}_{suffix}"
            for component in SOCIAL_SECURITY_COMPONENTS
            for suffix in ("joint_cola_factor", "pia_ratio_factor", "payable_factor")
        ),
    )
    simulation = make_simulation()
    for name in factor_names:
        assert system.variables[name].unit == "/1"
        assert amount(simulation, name, "2024-07") == 1
        assert amount(simulation, name, 2024) == 1
    supplied = simulation.get_branch("supplied_dimensionless_factors")
    for name in factor_names:
        supplied.set_input(name, 2024, [1.2])
    drop_inherited_values(supplied)
    for name in factor_names:
        assert amount(supplied, name, "2024-07") == pytest.approx(1.2)
        assert amount(supplied, name, 2024) == pytest.approx(1.2)


def test_original_component_dataset_columns_extend_once_by_per_capita_growth():
    base_amounts = dict(zip(SOCIAL_SECURITY_COMPONENTS, (24_000, 6_000, 3_000, 1_200)))
    group_entities = ("household", "tax_unit", "spm_unit", "family", "marital_unit")
    single = USSingleYearDataset(
        person=pd.DataFrame(
            {
                "person_id": [1],
                "age": [70],
                **{f"person_{entity}_id": [1] for entity in group_entities},
                **{name: [value] for name, value in base_amounts.items()},
            }
        ),
        household=pd.DataFrame({"household_id": [1], "household_weight": [1.0]}),
        tax_unit=pd.DataFrame({"tax_unit_id": [1]}),
        spm_unit=pd.DataFrame({"spm_unit_id": [1]}),
        family=pd.DataFrame({"family_id": [1]}),
        marital_unit=pd.DataFrame({"marital_unit_id": [1]}),
        time_period=2024,
    )
    # Independent expectation: national-total growth divided by population
    # growth exactly once, without using the dataset uprater's resolver.
    base_parameters = system.parameters("2024-01-01")
    projected_parameters = system.parameters("2025-01-01")
    national_growth = (
        projected_parameters.calibration.gov.irs.soi.social_security
        / base_parameters.calibration.gov.irs.soi.social_security
    )
    population_growth = (
        projected_parameters.calibration.gov.census.populations.total
        / base_parameters.calibration.gov.census.populations.total
    )
    per_person_growth = national_growth / population_growth
    extended = extend_single_year_dataset(single, end_year=2025, system=system)
    for public, base in base_amounts.items():
        assert single.person[public].iloc[0] == base
        assert extended[2024].person[public].iloc[0] == base
        assert extended[2025].person[public].iloc[0] == pytest.approx(
            base * per_person_growth, rel=1e-12
        )

    simulation = Microsimulation(dataset=extended, tax_benefit_system=system)
    for public, base in base_amounts.items():
        reported = f"{public}_reported"
        assert input_periods(simulation, public) == set()
        assert input_periods(simulation, reported) == {"2024", "2025"}
        for year, expected in ((2024, base), (2025, base * per_person_growth)):
            assert amount(simulation, public, f"{year}-07") == pytest.approx(
                expected / 12, rel=1e-6
            )
            assert amount(simulation, public, year) == pytest.approx(expected, rel=1e-6)
            assert amount(simulation, reported, year) == pytest.approx(
                expected, rel=1e-6
            )


def test_multi_year_microsimulation_uses_raw_source_and_fund_enums():
    from policyengine_core.reforms import Reform

    public = "social_security_dependents"
    multi_year = "year:2024:2"
    reform = Reform.from_dict(
        {
            "gov.contrib.ssa.benefit_levers.payable.share": {"2024": 0.8},
            "gov.contrib.ssa.benefit_levers.payable.oasi_only": {"2024": True},
        }
    )
    simulation = HouseholdMicrosimulation(
        situation=situation({f"{public}_base": {multi_year: 6_000}}),
        reform=reform,
        tax_benefit_system=system,
    )
    simulation.set_input("household_weight", multi_year, [1])
    # A positive exact base lacks annual base inputs. The adapter itself must
    # reject the unspecified enum, rather than comparing decoded display text.
    with pytest.raises(ValueError, match="dependent benefit fund"):
        simulation.calculate(public, multi_year)
    for fund, expected in (("di", 6_000), ("oasi", 4_800)):
        branch = simulation.get_branch(f"multi_year_{fund}")
        for year in (2024, 2025):
            branch.set_input(f"{public}_fund", year, [fund])
        drop_inherited_values(branch)
        assert amount(branch, public, multi_year) == pytest.approx(expected)
