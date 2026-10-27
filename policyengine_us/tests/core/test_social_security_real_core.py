"""Exercise source hooks on real Core storage, helpers and simulations.

This file deliberately does not import the country. Its tiny TaxBenefitSystem
uses the production hooks and installed Core implementations without stubs.
Run it separately from country-importing tests.
"""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import numpy as np
import pytest
from policyengine_core.entities import build_entity
from policyengine_core.experimental import MemoryConfig
from policyengine_core.holders import Holder, helpers
from policyengine_core.holders.helpers import (
    set_input_dispatch_by_period,
    set_input_divide_by_period,
)
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import period
from policyengine_core.simulations import Simulation, SimulationBuilder
from policyengine_core.taxbenefitsystems import TaxBenefitSystem
from policyengine_core.tools import simulation_dumper
from policyengine_core.variables import Variable
from policyengine_core.warnings import MemoryConfigWarning


COUNTRY_ROOT = Path(__file__).resolve().parents[2]
COMPONENTS = (
    "social_security_retirement",
    "social_security_disability",
    "social_security_survivors",
    "social_security_dependents",
)
PUBLIC = COMPONENTS[0]
hooks = None


@pytest.fixture(scope="module", autouse=True)
def installed_hooks():
    """Install only during execution and restore any pre-existing hooks.

    Collection never creates synthetic country packages. This also keeps
    grouped CI collection safe if another file imports the actual country.
    """
    global hooks
    targets = (Holder, Simulation, SimulationBuilder, helpers, simulation_dumper)
    originals = {target: dict(vars(target)) for target in targets}
    country_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "policyengine_us" or name.startswith("policyengine_us.")
    }
    synthetic_country = "policyengine_us" not in sys.modules
    try:
        if synthetic_country:
            # Make the production tools importable without executing the
            # country __init__, while retaining normal importlib.reload.
            for name, path in (
                ("policyengine_us", COUNTRY_ROOT),
                ("policyengine_us.tools", COUNTRY_ROOT / "tools"),
            ):
                package = types.ModuleType(name)
                package.__path__ = [str(path)]
                sys.modules[name] = package
        hooks = importlib.import_module("policyengine_us.tools.social_security_inputs")
        assert hooks.SOCIAL_SECURITY_COMPONENTS == COMPONENTS
        hooks.install_social_security_input_compatibility()
        yield
    finally:
        for target, previous in originals.items():
            for name in set(vars(target)) - previous.keys():
                delattr(target, name)
            for name, value in previous.items():
                if vars(target).get(name) is not value:
                    setattr(target, name, value)
        if synthetic_country:
            for name in tuple(sys.modules):
                if name == "policyengine_us" or name.startswith("policyengine_us."):
                    sys.modules.pop(name)
            sys.modules.update(country_modules)
        hooks = None


def make_system(*, enabled=True, factor=1):
    person = build_entity("person", "people", "Person", is_person=True)
    household = build_entity(
        "household",
        "households",
        "Household",
        roles=[{"key": "member", "plural": "members"}],
    )
    system = TaxBenefitSystem([person, household])
    system._social_security_input_compatibility = enabled
    system.auto_carry_over_input_variables = True
    system.parameters = ParameterNode(
        "",
        data={
            "fixture_index": {
                "values": {
                    "2023-01-01": 1,
                    "2024-01-01": 2,
                    "2025-01-01": 4,
                    "2026-01-01": 8,
                }
            }
        },
    )
    for component in COMPONENTS:
        for suffix in ("_reported", "_base", ""):
            name = component + suffix
            attributes = {
                "value_type": float,
                "label": name,
                "entity": person,
                "definition_period": "year",
                "__module__": __name__,
            }
            if suffix == "_reported":
                attributes["uprating"] = "fixture_index"
            elif suffix == "_base":

                def formula(person, period, parameters, component=component):
                    return person(component + "_reported", period)

                attributes["formula"] = formula
            elif not enabled:
                # Main's public source has uprating and no formula; the
                # adapter moves uprating to reported and makes public a formula.
                attributes["uprating"] = "fixture_index"
            else:

                def formula(person, period, parameters, component=component):
                    return person(component + "_base", period) * factor

                attributes["formula"] = formula
            system.add_variable(type(name, (Variable,), attributes))

    class independent_input(Variable):
        label = "Independent input"
        value_type = float
        entity = person
        definition_period = "year"

    class independent_formula(Variable):
        label = "Independent formula"
        value_type = float
        entity = person
        definition_period = "year"

        def formula(person, period, parameters):
            return person("independent_input", period) + 7

    system.add_variables(independent_input, independent_formula)
    return system


def fresh(inputs=None, *, enabled=True, factor=1):
    values = {"independent_input": {"2023": [70.0], "2024": [70.0]}}
    values.update(inputs or {})
    return SimulationBuilder().build_from_variables(
        make_system(enabled=enabled, factor=factor), values
    )


def fresh_without_holder_cache(mode, names, inputs=None):
    """Use each supported opt-out during Core's Holder initialization."""
    system = make_system()
    simulation = Simulation(
        tax_benefit_system=system, populations=system.instantiate_entities()
    )
    if mode == "blacklist":
        system.cache_blacklist = list(names)
        simulation.opt_out_cache = True
    else:
        assert mode == "variables_to_drop"
        with pytest.warns(MemoryConfigWarning):
            simulation.memory_config = MemoryConfig(
                1,
                # The tests exercise dropping, without introducing disk I/O.
                priority_variables=list(system.variables),
                variables_to_drop=names,
            )
    # Simulation.__init__ creates empty holders while enumerating its input
    # variables. Replace those populations so later Holder initialization
    # reads the actual memory_config rather than its constructor default.
    simulation.build_from_populations(system.instantiate_entities())
    values = {"independent_input": {"2023": [70.0], "2024": [70.0]}}
    values.update(inputs or {})
    return SimulationBuilder().build_from_variables(
        system, values, simulation=simulation
    )


def rebuild_with_source(simulation, value):
    from policyengine_core.data import Dataset

    class TinyDataset:
        data_format = Dataset.TIME_PERIOD_ARRAYS
        time_period = "2024"

        def load(self):
            return {
                "person_id": {"2024": np.array([1])},
                "household_id": {"2024": np.array([1])},
                "person_household_id": {"2024": np.array([1])},
                PUBLIC: {"2024": np.array([value])},
            }

    simulation.dataset = TinyDataset()
    simulation.build_from_dataset()


def scalar(simulation, name, requested):
    return float(simulation.calculate(name, requested)[0])


def stored(simulation, name, requested):
    return simulation.get_holder(name).get_array(
        period(requested), simulation.branch_name
    )


def earliest_source_dependency(simulation, component=PUBLIC, requested="2024"):
    history = simulation._get_store_history()
    candidates = [
        history.earliest_dependency(name, period(requested))
        for name in (component, component + "_reported")
    ]
    return min((number for number in candidates if number is not None), default=None)


def sequence_number(simulation, name, requested):
    holder = simulation.get_holder(name)
    return holder._memory_storage._sequence_numbers[
        f"{simulation.branch_name}:{period(requested)}"
    ]


HELPER_ROUTES = (
    ("divide", "year:2024:2", ("2024", "2025")),
    ("dispatch", "year:2024:2", ("2024", "2025")),
    ("ordinary_month", "month:2024-01:24", ("2024", "2025")),
    ("ordinary_year", "year:2024:2", ("2024", "2025")),
    (
        "rolling_month",
        "month:2024-07:24",
        ("year:2024-07", "year:2025-07"),
    ),
)


def apply_helper(simulation, component, route, compound):
    value = np.array([36_000.0])
    if route == "divide":
        set_input_divide_by_period(
            simulation.get_holder(component), period(compound), value
        )
    elif route == "dispatch":
        set_input_dispatch_by_period(
            simulation.get_holder(component), period(compound), value
        )
    else:
        simulation.set_input(component, compound, value)


@pytest.mark.parametrize("component", COMPONENTS)
@pytest.mark.parametrize("route,compound,annual", HELPER_ROUTES)
@pytest.mark.parametrize("initial", (False, True))
def test_compound_helpers_match_real_core(component, route, compound, annual, initial):
    inputs = {component: {annual[0]: [12_000.0]}} if initial else {}
    control = fresh(inputs, enabled=False)
    simulation = fresh(inputs)
    apply_helper(control, component, route, compound)
    apply_helper(simulation, component, route, compound)
    actual = [scalar(simulation, component, year) for year in annual]
    expected = [scalar(control, component, year) for year in annual]
    assert actual == expected
    # The source view must preserve the same allocation too, even where the
    # initial source stays hidden from the public formula's ordinary storage.
    assert [scalar(simulation, component + "_reported", year) for year in annual] == (
        expected
    )


def test_helper_keeps_initial_source_invisible_to_public_formula():
    simulation = fresh({PUBLIC: {"2024": [12_000.0]}}, factor=2)
    apply_helper(simulation, PUBLIC, "dispatch", "year:2024:2")
    assert stored(simulation, PUBLIC, "2024") is None
    assert scalar(simulation, PUBLIC + "_reported", "2024") == 12_000
    assert scalar(simulation, PUBLIC, "2024") == 24_000


def test_low_level_branch_write_preserves_raw_caller_seed():
    simulation = fresh({PUBLIC: {"2024": [12_000.0]}})
    branch = simulation.get_branch("child")
    assert scalar(branch, PUBLIC, "2026") == 48_000
    raw = branch.get_holder("independent_input")
    raw.put_in_cache(
        np.array([99.0]), period("2025"), branch.branch_name, derived=False
    )
    branch.get_holder(PUBLIC)._set(
        period("2024"), np.array([24_000.0]), branch.branch_name, is_input=True
    )
    np.testing.assert_array_equal(stored(branch, "independent_input", "2025"), [99])
    assert scalar(branch, PUBLIC, "2026") == 96_000


def test_bounded_refresh_preserves_derived_value_before_since():
    simulation = fresh()
    assert scalar(simulation, "independent_formula", "2023") == 77
    before = stored(simulation, "independent_formula", "2023")
    number = sequence_number(simulation, "independent_formula", "2023")
    simulation.set_input(PUBLIC, "2024", [12_000.0])
    assert scalar(simulation, PUBLIC + "_reported", "2026") == 48_000
    assert number < earliest_source_dependency(simulation)
    simulation.set_input(PUBLIC, "2024", [24_000.0])
    assert stored(simulation, "independent_formula", "2023") is before
    assert scalar(simulation, PUBLIC + "_reported", "2026") == 96_000


def test_bounded_refresh_intentionally_drops_derived_value_after_since():
    simulation = fresh({PUBLIC: {"2024": [12_000.0]}})
    assert scalar(simulation, PUBLIC + "_reported", "2026") == 48_000
    assert scalar(simulation, "independent_formula", "2024") == 77
    assert sequence_number(
        simulation, "independent_formula", "2024"
    ) >= earliest_source_dependency(simulation)
    epoch = simulation._input_epoch
    simulation.set_input(PUBLIC, "2024", [24_000.0])
    # Intended over-approximation: RULING-10400-refresh-scope-2026-10-26,
    # rule 5 permits unrelated formula values numbered at or after since.
    assert stored(simulation, "independent_formula", "2024") is None
    assert ("independent_formula", period("2024")) not in simulation._fast_cache
    assert simulation._input_epoch > epoch
    assert scalar(simulation, "independent_formula", "2024") == 77


def test_bounded_refresh_considers_reported_twin_history():
    simulation = fresh({PUBLIC + "_reported": {"2024": [6_000.0]}})
    assert scalar(simulation, "independent_formula", "2024") == 77
    history = simulation._get_store_history()
    assert history.earliest_dependency(PUBLIC, period("2024")) is None
    assert history.earliest_dependency(PUBLIC + "_reported", period("2024")) is not None
    simulation.set_input(PUBLIC, "2024", [12_000.0])
    assert stored(simulation, "independent_formula", "2024") is None
    assert scalar(simulation, PUBLIC + "_reported", "2024") == 6_000


@pytest.mark.parametrize("registered", (False, True), ids=("raw_seed", "input"))
def test_bounded_refresh_preserves_caller_values_after_since(registered):
    simulation = fresh({PUBLIC: {"2024": [12_000.0]}})
    scalar(simulation, PUBLIC + "_reported", "2026")
    holder = simulation.get_holder("independent_input")
    if registered:
        simulation.set_input("independent_input", "2025", [99.0])
    else:
        holder.put_in_cache(np.array([99.0]), period("2025"), derived=False)
    assert sequence_number(
        simulation, "independent_input", "2025"
    ) >= earliest_source_dependency(simulation)
    simulation.set_input(PUBLIC, "2024", [24_000.0])
    np.testing.assert_array_equal(stored(simulation, "independent_input", "2025"), [99])
    assert not holder.is_derived(period("2025"))
    assert holder._is_input(period("2025")) is registered


def test_reviewer_77_probe_has_no_source_dependency_and_keeps_fast_cache():
    simulation = fresh()
    assert scalar(simulation, "independent_formula", "2024") == 77
    value = stored(simulation, "independent_formula", "2024")
    fast_cache = dict(simulation._fast_cache)
    assert earliest_source_dependency(simulation) is None
    epoch = simulation._input_epoch
    simulation.set_input(PUBLIC, "2024", [12_000.0])
    # This is the reviewer's 77 probe: no source has been read, so there is
    # no since and the adapter must drop nothing, including fast-cache data.
    assert stored(simulation, "independent_formula", "2024") is value
    assert simulation._input_epoch == epoch
    for key, cached in fast_cache.items():
        assert simulation._fast_cache[key] is cached


def test_reload_reinstall_write_and_read():
    simulation = fresh({PUBLIC: {"2024": [12_000.0]}})
    importlib.reload(hooks)
    hooks.install_social_security_input_compatibility()
    simulation.set_input(PUBLIC, "2024", [24_000.0])
    assert scalar(simulation, PUBLIC + "_reported", "2024") == 24_000
    assert scalar(simulation, PUBLIC, "2024") == 24_000


@pytest.mark.parametrize("warm_source", (False, True))
def test_dataset_rebuild_refreshes_discarded_holder_caches(warm_source):
    from policyengine_core.data import Dataset

    simulation = fresh()
    assert scalar(simulation, "independent_formula", "2023") == 77
    independent_holder = simulation.get_holder("independent_formula")
    independent_key = ("independent_formula", period("2023"))
    independent_fast = simulation._fast_cache[independent_key]
    if warm_source:
        assert scalar(simulation, PUBLIC, "2023") == 0

    class TinyDataset:
        data_format = Dataset.TIME_PERIOD_ARRAYS
        time_period = "2023"

        def load(self):
            return {
                "person_id": {"2023": np.array([1])},
                "household_id": {"2023": np.array([1])},
                "person_household_id": {"2023": np.array([1])},
                PUBLIC: {"2023": np.array([1.0])},
            }

    simulation.dataset = TinyDataset()
    simulation.build_from_dataset()
    assert scalar(simulation, PUBLIC + "_reported", "2023") == 1
    assert scalar(simulation, PUBLIC, "2023") == 1
    # Core replaces populations during dataset loading. Retain its former
    # holder here to audit the adapter's treatment of the detached cache.
    assert float(independent_holder.get_array(period("2023"))[0]) == 77
    if not warm_source:
        # No source read means no cutoff and no adapter eviction, including
        # a cached reader whose former holder Core itself has detached.
        assert simulation._fast_cache[independent_key] is independent_fast


def test_dataset_rebuild_keeps_new_input_provenance_when_old_cache_shares_key():
    from policyengine_core.data import Dataset

    simulation = SimulationBuilder().build_from_variables(make_system(), {})
    assert scalar(simulation, PUBLIC, "2023") == 0
    since = earliest_source_dependency(simulation, requested="2023")
    assert since is not None
    assert scalar(simulation, "independent_input", "2023") == 0
    old_holder = simulation.get_holder("independent_input")
    assert old_holder.is_derived(period("2023"))
    assert sequence_number(simulation, "independent_input", "2023") >= since

    class TinyDataset:
        data_format = Dataset.TIME_PERIOD_ARRAYS
        time_period = "2023"

        def load(self):
            return {
                "person_id": {"2023": np.array([1])},
                "household_id": {"2023": np.array([1])},
                "person_household_id": {"2023": np.array([1])},
                # Store this before the benefit write so an old derived
                # cache with the same key cannot unregister the new input.
                "independent_input": {"2023": np.array([99.0])},
                PUBLIC: {"2023": np.array([1.0])},
            }

    simulation.dataset = TinyDataset()
    simulation.build_from_dataset()
    current_holder = simulation.get_holder("independent_input")
    assert current_holder is not old_holder
    np.testing.assert_array_equal(stored(simulation, "independent_input", "2023"), [99])
    assert current_holder._is_input(period("2023"))
    assert period("2023") in simulation._get_set_input_periods("independent_input")
    snapshot = hooks.export_source_inputs(simulation)
    person = next(iter(snapshot["sources"]["people"].values()))
    assert person["independent_input"]["2023"] == 99
    assert scalar(simulation, PUBLIC, "2023") == 1


@pytest.mark.parametrize("mode", ("blacklist", "variables_to_drop"))
@pytest.mark.parametrize(
    "route,source",
    (
        ("dataset", PUBLIC),
        ("set_input", PUBLIC),
        ("set_input", PUBLIC + "_reported"),
        ("branch_set", PUBLIC),
        ("branch_set", PUBLIC + "_reported"),
    ),
    ids=(
        "dataset_public",
        "set_public",
        "set_reported",
        "branch_public",
        "branch_reported",
    ),
)
@pytest.mark.parametrize("initial", (0, 12_000), ids=("default_zero", "initial_source"))
def test_source_write_refreshes_fast_only_formula_returns(mode, route, source, initial):
    names = [PUBLIC, PUBLIC + "_base"]
    if not initial:
        # The review's zero-source variant also opts the reported default out.
        names.append(PUBLIC + "_reported")
    inputs = {PUBLIC: {"2024": [initial]}} if initial else {}
    simulation = fresh_without_holder_cache(mode, names, inputs)
    if route == "branch_set":
        simulation = simulation.get_branch("child")
    assert scalar(simulation, PUBLIC, "2024") == initial
    assert earliest_source_dependency(simulation) is not None
    assert stored(simulation, PUBLIC, "2024") is None
    assert stored(simulation, PUBLIC + "_base", "2024") is None
    key = (PUBLIC, period("2024"))
    assert float(simulation._fast_cache[key][0]) == initial
    epoch = simulation._input_epoch
    if route == "dataset":
        rebuild_with_source(simulation, 24_000.0)
    elif route == "set_input":
        simulation.set_input(source, "2024", [24_000.0])
    else:
        # Exercise the adapter itself: Core adds dependency cleanup only on
        # Holder.set_input, not on this supported lower-level branch route.
        simulation.get_holder(source)._set(
            period("2024"),
            np.array([24_000.0]),
            simulation.branch_name,
            is_input=True,
        )
    memo_survived_write = key in simulation._fast_cache
    reported_after = scalar(simulation, PUBLIC + "_reported", "2024")
    public_after = scalar(simulation, PUBLIC, "2024")
    assert (reported_after, public_after) == (24_000, 24_000)
    assert not memo_survived_write
    assert simulation._input_epoch > epoch


@pytest.mark.parametrize("mode", ("blacklist", "variables_to_drop"))
def test_fast_only_formula_before_since_survives_without_a_drop_witness(mode):
    simulation = fresh_without_holder_cache(mode, ["independent_formula"])
    assert scalar(simulation, "independent_formula", "2023") == 77
    key = ("independent_formula", period("2023"))
    before = simulation._fast_cache[key]
    assert stored(simulation, "independent_formula", "2023") is None
    number = simulation._get_store_history().earliest_dependency(*key)
    simulation.set_input(PUBLIC, "2024", [12_000.0])
    assert scalar(simulation, PUBLIC + "_reported", "2024") == 12_000
    assert number < earliest_source_dependency(simulation)
    epoch = simulation._input_epoch
    simulation.set_input(PUBLIC, "2024", [24_000.0])
    # A pre-cutoff fast-only return cannot itself justify a global clear.
    assert simulation._fast_cache[key] is before
    assert simulation._input_epoch == epoch
    assert scalar(simulation, "independent_formula", "2023") == 77


@pytest.mark.parametrize("mode", ("blacklist", "variables_to_drop"))
def test_fast_only_unrelated_formula_after_since_is_intentionally_dropped(mode):
    simulation = fresh_without_holder_cache(
        mode, ["independent_formula"], {PUBLIC: {"2024": [12_000.0]}}
    )
    assert scalar(simulation, PUBLIC + "_reported", "2024") == 12_000
    assert scalar(simulation, "independent_formula", "2024") == 77
    key = ("independent_formula", period("2024"))
    assert stored(simulation, *key) is None
    assert simulation._get_store_history().earliest_dependency(
        *key
    ) >= earliest_source_dependency(simulation)
    epoch = simulation._input_epoch
    simulation.set_input(PUBLIC, "2024", [24_000.0])
    # Intended over-approximation: refresh-scope ruling rule 5 includes an
    # unrelated formula return whose own store number is after the cutoff.
    assert key not in simulation._fast_cache
    assert simulation._input_epoch > epoch
    assert scalar(simulation, "independent_formula", "2024") == 77


@pytest.mark.parametrize("mode", ("blacklist", "variables_to_drop"))
def test_recalculated_fast_only_return_uses_its_own_store_number(mode, monkeypatch):
    stores = []
    original_record_store = Holder._record_store

    def record_store(holder, requested, number):
        if holder.variable.name == "independent_formula":
            stores.append(number)
        return original_record_store(holder, requested, number)

    monkeypatch.setattr(Holder, "_record_store", record_store)
    simulation = fresh_without_holder_cache(mode, ["independent_formula"])
    assert scalar(simulation, "independent_formula", "2023") == 77
    key = ("independent_formula", period("2023"))
    first = simulation._get_store_history().earliest_dependency(*key)
    assert first == stores[-1]
    simulation.set_input(PUBLIC, "2024", [12_000.0])
    assert scalar(simulation, PUBLIC + "_reported", "2024") == 12_000
    since = earliest_source_dependency(simulation)
    assert first < since
    # Recompute the same key after the source cutoff. StoreHistory keeps its
    # first number, whereas the memo must be dated by this later calculation.
    simulation._fast_cache.pop(key)
    assert scalar(simulation, "independent_formula", "2023") == 77
    assert stores[-1] >= since
    assert simulation._get_store_history().earliest_dependency(*key) == first
    epoch = simulation._input_epoch
    simulation.set_input(PUBLIC, "2024", [24_000.0])
    assert key not in simulation._fast_cache
    assert simulation._input_epoch > epoch


@pytest.mark.parametrize("mode", ("blacklist", "variables_to_drop"))
@pytest.mark.parametrize("branch", (False, True), ids=("main", "branch"))
@pytest.mark.parametrize("registered", (False, True), ids=("raw_seed", "input"))
def test_not_kept_formula_name_preserves_physical_caller_values(
    mode, branch, registered
):
    names = [PUBLIC, PUBLIC + "_base", "independent_formula"]
    simulation = fresh_without_holder_cache(mode, names, {PUBLIC: {"2024": [12_000.0]}})
    if branch:
        simulation = simulation.get_branch("child")
    assert scalar(simulation, PUBLIC, "2024") == 12_000
    holder = simulation.get_holder("independent_formula")
    if registered:
        simulation.set_input("independent_formula", "2025", [99.0])
    else:
        # _set can supply a raw seed even where put_in_cache is opted out.
        holder._set(
            period("2025"),
            np.array([99.0]),
            simulation.branch_name,
            derived=False,
            is_input=False,
        )
    before = stored(simulation, "independent_formula", "2025")
    assert sequence_number(
        simulation, "independent_formula", "2025"
    ) >= earliest_source_dependency(simulation)
    assert not holder.is_derived(period("2025"), simulation.branch_name)
    epoch = simulation._input_epoch
    simulation.get_holder(PUBLIC)._set(
        period("2024"),
        np.array([24_000.0]),
        simulation.branch_name,
        is_input=True,
    )
    assert simulation._input_epoch > epoch
    assert stored(simulation, "independent_formula", "2025") is before
    assert holder._is_input(period("2025"), simulation.branch_name) is registered
    assert scalar(simulation, "independent_formula", "2025") == 99
    assert scalar(simulation, PUBLIC, "2024") == 24_000


@pytest.mark.parametrize("mode", ("blacklist", "variables_to_drop"))
def test_unread_source_load_preserves_fast_only_returns_without_a_cutoff(mode):
    names = [PUBLIC, PUBLIC + "_base", PUBLIC + "_reported", "independent_formula"]
    simulation = fresh_without_holder_cache(mode, names)
    assert scalar(simulation, "independent_formula", "2023") == 77
    key = ("independent_formula", period("2023"))
    before = simulation._fast_cache[key]
    assert earliest_source_dependency(simulation) is None
    epoch = simulation._input_epoch
    rebuild_with_source(simulation, 24_000.0)
    assert simulation._input_epoch == epoch
    assert simulation._fast_cache[key] is before
    assert scalar(simulation, PUBLIC, "2024") == 24_000


@pytest.mark.parametrize("initial", (False, True), ids=("raw_source", "initial_source"))
def test_exact_reported_read_bypasses_native_memo_and_keeps_other_caches(initial):
    simulation = fresh()
    assert scalar(simulation, "independent_formula", "2024") == 77
    independent_key = ("independent_formula", period("2024"))
    independent_fast = simulation._fast_cache[independent_key]
    if initial:
        SimulationBuilder().build_from_variables(
            simulation.tax_benefit_system,
            {PUBLIC: {"2024": [12_000.0]}},
            simulation=simulation,
        )
    else:
        simulation.get_holder(PUBLIC).put_in_cache(
            np.array([12_000.0]), period("2024"), derived=False
        )
    assert scalar(simulation, PUBLIC + "_reported", "2024") == 12_000
    # Native Core returns this exact source directly from get_array; unlike
    # the synthetic backend, neither supported Core version inserts a memo.
    reported_key = (PUBLIC + "_reported", period("2024"))
    assert reported_key not in simulation._fast_cache
    # This exact read returns the source view without storing a derived
    # reported array. There is no post-cutoff formula array to purge.
    assert (
        simulation.get_holder(PUBLIC + "_reported")._memory_storage.get(period("2024"))
        is None
    )
    epoch = simulation._input_epoch
    simulation.set_input(PUBLIC, "2024", [24_000.0])
    assert scalar(simulation, PUBLIC + "_reported", "2024") == 24_000
    assert simulation._fast_cache[independent_key] is independent_fast
    assert stored(simulation, "independent_formula", "2024") is independent_fast
    assert simulation._input_epoch == epoch


if __name__ == "__main__":
    raise SystemExit(
        pytest.main([__file__, "-q", "--confcutdir", str(Path(__file__).parent)])
    )
