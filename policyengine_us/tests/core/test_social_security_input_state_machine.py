"""Search compositions of public and reported Social Security input routes.

Property: a reported source uses an explicit input at or before its requested
period; otherwise its read-time view follows the latest public input. Exact
compound totals keep their own period semantics. Copies preserve those
sources and public final overrides, while later writes remain isolated.
After every step, actual Core readers must return the independently modeled
reported amount and public formula amount, including the initial scored year
and a later year whose intermediate base may already have been cached.

The backend executes installed Core source bodies and the production US hooks
without importing the country. Run this file directly for a country-free test:
``python policyengine_us/tests/core/test_social_security_input_state_machine.py``.
"""

from __future__ import annotations

import copy
import importlib.util
import sys
import tempfile
import unittest
from dataclasses import dataclass, field
from pathlib import Path

from hypothesis import HealthCheck, settings, strategies as st
from hypothesis.stateful import (
    RuleBasedStateMachine,
    initialize,
    invariant,
    precondition,
    rule,
)


spec = importlib.util.spec_from_file_location(
    "_social_security_state_backend",
    Path(__file__).with_name("_social_security_state_backend.py"),
)
backend_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = backend_module
spec.loader.exec_module(backend_module)
Backend = backend_module.Backend
COMPONENTS = backend_module.COMPONENTS
as_period = backend_module.as_period

COMPONENT = st.sampled_from(COMPONENTS)
PERIOD = st.sampled_from(("2023", "2024", "2025", "year:2023:2", "year:2024:2"))
AMOUNT = st.integers(min_value=0, max_value=48_000)
TARGET = st.integers(min_value=0, max_value=31)
CACHE_NAMES = (
    *COMPONENTS,
    *(f"{name}_base" for name in COMPONENTS),
    *(f"{name}_reported" for name in COMPONENTS),
    "unrelated_formula",
)
CACHE_CONFIGURATION = st.tuples(
    st.sampled_from(("blacklist", "variables_to_drop")),
    st.sets(st.sampled_from(CACHE_NAMES), min_size=1),
)


@dataclass
class Input:
    amount: int
    registered: bool
    route: str


@dataclass
class Model:
    # Caller inputs are distinct slots on each branch. A raw branch write
    # hides, rather than erases, an inherited registered input.
    public: dict = field(default_factory=dict)
    explicit: dict = field(default_factory=dict)
    overrides: dict = field(default_factory=dict)
    branch_name: str = "default"
    visible_branches: tuple = ("default",)

    def keys(self):
        return {
            (component, period)
            for mapping in (self.public, self.explicit, self.overrides)
            for branch, component, period in mapping
            if branch in self.visible_branches
        }

    def visible(self, mapping, component, period):
        return next(
            (
                mapping[(branch, component, period)]
                for branch in self.visible_branches
                if (branch, component, period) in mapping
            ),
            None,
        )

    def reported(self, component, period):
        explicit = self.visible(self.explicit, component, period)
        if explicit is not None:
            return explicit, False
        requested = as_period(period)
        for other_component, known in self.keys():
            candidate = as_period(known)
            if (
                other_component == component
                and (
                    candidate.start <= requested.start
                    if requested.size == 1
                    else candidate == requested
                )
                and self.visible(self.explicit, component, known) is not None
            ):
                # Core uprates from the earlier explicit source. It must not
                # see a same-period public fallback as a newer reported input.
                return None, False
        return self.visible(self.public, component, period), True

    def reader_source(self, component, period):
        """The source an annual reader selects, independently of Core storage."""
        requested = as_period(period)
        explicit = {
            known: value
            for other_component, known in self.keys()
            if other_component == component
            and as_period(known).start <= requested.start
            and (value := self.visible(self.explicit, component, known)) is not None
        }
        mapping = self.explicit if explicit else self.public
        candidates = explicit or {
            known: value
            for other_component, known in self.keys()
            if other_component == component
            and as_period(known).start <= requested.start
            and (value := self.visible(mapping, component, known)) is not None
        }
        if period in candidates:
            return candidates[period], period, not bool(explicit)
        if not candidates:
            return None, None, False
        # Core first uprates an input starting strictly before the request.
        # Only when none exists does carry-over consider a compound input
        # starting in the requested year.
        earlier = {
            known: value
            for known, value in candidates.items()
            if as_period(known).start < requested.start
        }
        known = max(
            earlier or candidates,
            key=lambda text: (
                as_period(text).start,
                as_period(text).stop,
                text,
            ),
        )
        return candidates[known], known, not bool(explicit)

    def reader_amount(self, component, period):
        value, known, _ = self.reader_source(component, period)
        if value is None:
            return 0
        return value.amount * 2 ** (
            as_period(period).start.year - as_period(known).start.year
        )

    def drop_overlapping_raw(self, component, reported, period):
        """Model Core's newer cleanup of non-input overlapping cache seeds.

        This follows the same rule as main: a raw cache is a carry seed while
        it survives, but an overlapping registered set_input may remove it.
        Reserved initial sources are registered inputs and are retained.
        """
        requested = as_period(period)
        for name in ("explicit",) if reported else ("public", "overrides"):
            mapping = getattr(self, name)
            for key, value in tuple(mapping.items()):
                branch, other_component, known = key
                candidate = as_period(known)
                if (
                    branch in self.visible_branches
                    and other_component == component
                    and not value.registered
                    and candidate.start <= requested.stop
                    and candidate.stop >= requested.start
                ):
                    del mapping[key]

    def write(
        self,
        component,
        reported,
        period,
        amount,
        registered,
        route,
        initial=False,
        branch_name=None,
        cleanup=False,
    ):
        if cleanup:
            self.drop_overlapping_raw(component, reported, period)
        branch_name = self.branch_name if branch_name is None else branch_name
        key = (branch_name, component, period)
        value = Input(amount, registered, route)
        if reported:
            self.explicit[key] = value
        else:
            self.public[key] = value
            if initial and self.visible(self.explicit, component, period) is None:
                # Initial migration removes visible public slots, including
                # a superseded inherited final override for the same period.
                for branch in self.visible_branches:
                    self.overrides.pop((branch, component, period), None)
            else:
                self.overrides[key] = value

    def keep_registered(self):
        for name in ("public", "explicit", "overrides"):
            setattr(
                self,
                name,
                {
                    key: value
                    for key, value in getattr(self, name).items()
                    if value.registered
                },
            )

    def flatten(self, promote_raw=False):
        keys = self.keys()
        for name in ("public", "explicit", "overrides"):
            mapping = getattr(self, name)
            flat = {}
            for component, period in keys:
                value = self.visible(mapping, component, period)
                if value is not None:
                    value = copy.deepcopy(value)
                    if promote_raw:
                        value.registered = True
                    flat[("default", component, period)] = value
            setattr(self, name, flat)
        self.branch_name = "default"
        self.visible_branches = ("default",)


class SocialSecurityInputsMachine(RuleBasedStateMachine):
    """All writes may target earlier clones, branches, or restored copies."""

    def __init__(self):
        super().__init__()
        self.backend = None
        self.states = []
        self.temp = tempfile.TemporaryDirectory(prefix="ss-input-machine-")
        self.dump_count = 0
        self.branch_initial_rewrite_done = False
        self.preservation_checks = []
        self.helper_checks = []

    @initialize(cache_configuration=CACHE_CONFIGURATION)
    def configure_cache(self, cache_configuration):
        """Search Core's two policies that number returns without storing arrays."""
        mode, names = cache_configuration
        self.backend = Backend(
            cache_blacklist=names if mode == "blacklist" else (),
            variables_to_drop=names if mode == "variables_to_drop" else (),
        )
        self.states = [(self.backend.DelegatingSimulation(), Model())]

    def teardown(self):
        self.temp.cleanup()
        if self.backend is not None:
            self.backend.close()

    def state(self, slot):
        return self.states[slot % len(self.states)]

    @staticmethod
    def name(component, reported):
        return f"{component}_reported" if reported else component

    def append(self, simulation, model):
        self.states.append((simulation, model))

    @staticmethod
    def write_key(model, component, period, data):
        # Reuse caller-known slots as well as drawing fresh ones. This makes
        # collisions between independent routes, copies and replay common.
        keys = sorted(model.keys())
        if (
            data is not None
            and keys
            and data.draw(st.booleans(), label="reuse existing input")
        ):
            return data.draw(
                st.sampled_from(keys), label="existing component and period"
            )
        return component, period

    def prepare_core_input_drop(self, simulation, model, name, period, amount):
        """Model Core's own branch drop, including its raw-seed behavior.

        Core first reclassifies all nonregistered values as derived; only
        registered inputs remain eligible sources after such a drop.
        Low-level adapter writes deliberately never call this method.
        """
        if simulation.parent_branch is None:
            return
        holder = simulation.get_holder(name)
        if holder._input_unchanged(as_period(period), [amount], simulation.branch_name):
            return
        since = simulation._get_store_history().earliest_dependency(
            name, as_period(period)
        )
        if holder._has_unnumbered_values():
            since = 0
        if since is None:
            return
        for mapping in (model.public, model.explicit, model.overrides):
            for key, value in tuple(mapping.items()):
                if not value.registered:
                    # Core first reclassifies every nonregistered seed as
                    # derived, even when its sequence is before the cutoff.
                    # It no longer supplies a source to uprating/carry-over.
                    del mapping[key]

    @rule(
        component=COMPONENT,
        helper=st.sampled_from(("divide", "dispatch", "ordinary")),
        compound=st.sampled_from(("year:2024:2", "month:2024-01:24", "year:2024-07:2")),
        initial=st.booleans(),
        amount=st.integers(min_value=24_000, max_value=48_000),
    )
    def initial_source_then_period_helper(
        self, component, helper, compound, initial, amount
    ):
        """Compare each allocation with Core running without the adapter."""
        if helper == "ordinary":
            compound = "month:2024-01:24"
        inputs = {component: {"2024": [12_000]}} if initial else {}
        adapted = self.backend.Builder().build_from_variables(
            self.backend.system, inputs
        )
        self.backend.system._social_security_input_compatibility = False
        try:
            plain = self.backend.Builder().build_from_variables(
                self.backend.system, inputs
            )
            self.apply_helper(plain, component, helper, compound, amount)
        finally:
            self.backend.system._social_security_input_compatibility = True
        self.apply_helper(adapted, component, helper, compound, amount)
        period = as_period(compound)
        branch = adapted.branch_name
        # The fixture's public formula multiplies its initial source by two.
        # Compare allocations through Core's input lookup, which is the
        # source the helper must see, rather than that reform factor.
        years = []
        allocation_model = Model()
        if initial:
            allocation_model.write(
                component,
                False,
                "2024",
                12_000,
                True,
                "initial helper source",
                initial=True,
            )
        subperiod = period.start.period("year")
        stop = period.start.offset(period.size, period.unit)
        while subperiod.start < stop:
            expected = self.backend.helpers.get_stored_input(
                plain.get_holder(component), subperiod, plain.branch_name
            )
            actual = self.backend.helpers.get_stored_input(
                adapted.get_holder(component), subperiod, branch
            )
            assert expected is not None and actual is not None
            self.helper_checks.append(
                (adapted, component, subperiod, expected.copy(), compound)
            )
            years.append(subperiod)
            if not (initial and str(subperiod) == "2024"):
                allocation_model.write(
                    component,
                    False,
                    str(subperiod),
                    float(expected[0]),
                    True,
                    "Core helper",
                )
            subperiod = subperiod.offset(1)
        # Exercise a real compound calculation after allocations. Core's
        # calculate_add sums annual subperiod readers instead of fabricating
        # an exact total source for the compound.
        actual_total = (
            float(adapted.calculate_add(component, period)[0])
            if period.unit == "year"
            else sum(float(adapted.calculate(component, year)[0]) for year in years)
        )
        calculation_years = (
            period.get_subperiods("year") if period.unit == "year" else years
        )
        expected_total = 0
        for year in calculation_years:
            override = allocation_model.visible(
                allocation_model.overrides, component, str(year)
            )
            expected_total += (
                override.amount
                if override is not None
                else allocation_model.reader_amount(component, str(year)) * 2
            )
        assert actual_total == expected_total

    def apply_helper(self, simulation, component, helper, compound, amount):
        if helper == "ordinary":
            simulation.set_input(component, compound, [amount])
        else:
            function = getattr(self.backend.helpers, f"set_input_{helper}_by_period")
            function(simulation.get_holder(component), as_period(compound), [amount])

    @rule(component=COMPONENT, partly_failing=st.booleans())
    def custom_input_handler_after_initial_source(self, component, partly_failing):
        simulation = self.backend.Builder().build_from_variables(
            self.backend.system, {component: {"2024": [12_000]}}
        )
        variable = self.backend.system.get_variable(component)
        original = variable.set_input
        failure = RuntimeError("intentional partial input handler failure")

        def handler(holder, period, amount):
            if partly_failing:
                holder._set(as_period("2025"), [24_000], is_input=True)
                # Calculations inside a handler must not preserve old readers
                # when the handler subsequently raises after a successful store.
                holder.simulation.calculate(component, as_period("2026"))
                raise failure
            self.backend.helpers.set_input_divide_by_period(holder, period, amount)

        variable.set_input = handler
        try:
            try:
                simulation.set_input(component, "month:2024-01:24", [36_000])
            except RuntimeError as caught:
                assert partly_failing and caught is failure
            else:
                assert not partly_failing
        finally:
            variable.set_input = original
        self.preservation_checks.append(
            (simulation, component + "_reported", "2024", 12_000)
        )
        self.preservation_checks.append((simulation, component, "2025", 24_000))

    @rule(component=COMPONENT)
    def deleting_explicit_source_reveals_initial_source(self, component):
        simulation = self.backend.Builder().build_from_variables(
            self.backend.system, {component: {"2024": [12_000]}}
        )
        reported = component + "_reported"
        simulation.set_input(reported, "2024", [6_000])
        assert float(simulation.calculate(reported, as_period("2024"))[0]) == 6_000
        simulation.get_holder(reported).delete_arrays(as_period("2024"))
        # A source read resolves current physical tiers after the deletion.
        value = simulation.get_holder(reported).get_array(as_period("2024"))
        assert value is not None and float(value[0]) == 12_000

    @rule(component=COMPONENT, branch=st.booleans(), read_source=st.booleans())
    def bounded_refresh_preserves_caller_values(self, component, branch, read_source):
        """Keep pre-cutoff formulas, raw seeds and supplied inputs on every write."""
        simulation = self.backend.DelegatingSimulation()
        early = simulation.get_holder("early_derived")
        early.put_in_cache([77], as_period("2025"), derived=True)
        if read_source:
            simulation.set_input(component, "2024", [12_000])
        if branch:
            simulation = simulation.get_branch("preservation")
        if read_source:
            simulation.calculate(component, as_period("2026"))
        raw = simulation.get_holder("raw_seed")
        raw.put_in_cache([99], as_period("2025"), simulation.branch_name, derived=False)
        simulation.set_input("independent_input", "2025", [88])
        late = simulation.get_holder("late_derived")
        late.put_in_cache([55], as_period("2025"), simulation.branch_name, derived=True)
        since = simulation._get_store_history().earliest_dependency(
            component, as_period("2024")
        )
        simulation.get_holder(component)._set(
            as_period("2024"), [24_000], simulation.branch_name, is_input=True
        )
        for name, expected in (
            ("early_derived", 77),
            ("raw_seed", 99),
            ("independent_input", 88),
        ):
            self.preservation_checks.append((simulation, name, "2025", expected))
        if since is not None:
            # Intended over-approximation: the refresh-scope ruling allows
            # an unrelated formula numbered at or after since to be dropped.
            assert late.get_array(as_period("2025"), simulation.branch_name) is None
        else:
            self.preservation_checks.append((simulation, "late_derived", "2025", 55))

    @invariant()
    def caller_values_and_earlier_derived_survive(self):
        for simulation, name, period, expected in self.preservation_checks:
            value = simulation.get_holder(name).get_array(
                as_period(period), simulation.branch_name
            )
            assert value is not None and float(value[0]) == expected, (
                name,
                period,
                "adapter removed a caller value or pre-cutoff formula",
            )
        for simulation, component, period, expected, compound in self.helper_checks:
            actual = self.backend.helpers.get_stored_input(
                simulation.get_holder(component), period, simulation.branch_name
            )
            assert actual is not None and (actual == expected).all(), (
                component,
                compound,
                "Core helper allocation",
            )

    @rule(
        slot=TARGET,
        component=COMPONENT,
        reported=st.booleans(),
        period=PERIOD,
        amount=AMOUNT,
        data=st.data(),
        route=st.sampled_from(("simulation", "holder", "delegating")),
    )
    def set_input(self, slot, component, reported, period, amount, route, data=None):
        simulation, model = self.state(slot)
        component, period = self.write_key(model, component, period, data)
        name = self.name(component, reported)
        self.prepare_core_input_drop(simulation, model, name, period, amount)
        if route == "holder":
            simulation.get_holder(name).set_input(
                as_period(period), [amount], simulation.branch_name
            )
        else:
            # All live instances are delegating subclasses or genuine Core
            # copies thereof; explicitly invoke Core for its separate route.
            setter = (
                self.backend.Simulation.set_input
                if route == "simulation"
                else type(simulation).set_input
            )
            setter(simulation, name, period, [amount])
        model.write(
            component,
            reported,
            period,
            amount,
            True,
            route,
            cleanup=self.backend.cleans_raw_overlaps,
        )

    @rule(
        slot=TARGET,
        component=COMPONENT,
        reported=st.booleans(),
        period=PERIOD,
        amount=AMOUNT,
        data=st.data(),
        is_input=st.sampled_from((None, False, True)),
        in_context=st.booleans(),
        default_branch_argument=st.booleans(),
    )
    def low_level_store(
        self,
        slot,
        component,
        reported,
        period,
        amount,
        is_input,
        in_context,
        default_branch_argument,
        data=None,
    ):
        simulation, model = self.state(slot)
        component, period = self.write_key(model, component, period, data)
        if in_context:
            simulation._user_input_contexts.append(simulation.branch_name)
        try:
            # Core redirects default to an active input context for registered
            # stores. Exercise both implicit and explicit branch selection.
            branch_argument = (
                "default"
                if default_branch_argument and in_context and is_input is not False
                else simulation.branch_name
            )
            simulation.get_holder(self.name(component, reported))._set(
                as_period(period), [amount], branch_argument, is_input=is_input
            )
        finally:
            if in_context:
                simulation._user_input_contexts.pop()
        registered = in_context if is_input is None else is_input
        model.write(
            component,
            reported,
            period,
            amount,
            registered,
            f"_set({is_input}, context={in_context})",
        )

    @rule(
        slot=TARGET,
        component=COMPONENT,
        reported=st.booleans(),
        period=PERIOD,
        amount=AMOUNT,
        data=st.data(),
    )
    def nonderived_cache(self, slot, component, reported, period, amount, data=None):
        simulation, model = self.state(slot)
        component, period = self.write_key(model, component, period, data)
        holder = simulation.get_holder(self.name(component, reported))
        holder.put_in_cache(
            [amount], as_period(period), simulation.branch_name, derived=False
        )
        # Core's put_in_cache ignores nonderived seeds too under these
        # policies. A raw _set still stores and is covered by low_level_store.
        if not (
            holder._do_not_store
            or (
                simulation.opt_out_cache
                and holder.variable.name
                in simulation.tax_benefit_system.cache_blacklist
            )
        ):
            model.write(component, reported, period, amount, False, "put_in_cache")

    @rule(
        slot=TARGET,
        component=COMPONENT,
        reported=st.booleans(),
        period=PERIOD,
        amount=AMOUNT,
        data=st.data(),
        derived=st.booleans(),
    )
    def cache_result(
        self, slot, component, reported, period, amount, derived, data=None
    ):
        """Calculated values must not acquire reported-source provenance."""
        if not derived:
            return
        simulation, model = self.state(slot)
        component, period = self.write_key(model, component, period, data)
        # Cache an actual reader result. An arbitrary fabricated formula
        # result could disagree with its own source by construction; this
        # rule instead checks that real derived results never become sources.
        name = self.name(component, reported)
        if as_period(period).size > 1:
            period = str(as_period(period).start.year)
        value = simulation.calculate(name, as_period(period))
        simulation.get_holder(name).put_in_cache(
            value, as_period(period), simulation.branch_name, derived=True
        )

    @rule(slot=TARGET, name=st.sampled_from(CACHE_NAMES))
    def bulk_delete_formula_cache(self, slot, name):
        """Exercise Core's replacement of the memo dict around other returns."""
        simulation, _ = self.state(slot)
        holder = simulation.get_holder(name)
        visible = set(simulation._get_visible_branch_names())
        if any(
            branch in visible and not storage.is_derived(period, branch)
            for storage in (holder._memory_storage, holder._disk_storage)
            if storage is not None
            for branch, period in storage.get_known_branch_periods()
        ):
            # Delete formula caches, preserving this machine's caller source
            # model. Core's delete API does not refresh dependent formulas
            # after deleting caller inputs; source writes are separate rules.
            return
        simulation.delete_arrays(name)

    @rule(
        component=COMPONENT,
        name=st.sampled_from(CACHE_NAMES),
        amount=st.integers(min_value=12_001, max_value=48_000),
    )
    def bulk_delete_then_reported_write(self, component, name, amount):
        """Compose a replaced memo with a later source write before other reads."""
        simulation = self.backend.Builder().build_from_variables(
            self.backend.system, {component: {"2024": [12_000]}}
        )
        model = Model()
        model.write(component, False, "2024", 12_000, True, "builder", initial=True)
        assert float(simulation.calculate(component, as_period("2024"))[0]) == 24_000
        simulation.delete_arrays(name)
        # Initial public inputs are on reserved source branches, outside
        # Core's visible-branch bulk deletion. Every generated name therefore
        # deletes only formula caches here, keeping the caller model intact.
        source = simulation.get_holder(f"{component}_reported").get_array(
            as_period("2024"), simulation.branch_name
        )
        assert source is not None and float(source[0]) == 12_000
        simulation.set_input(f"{component}_reported", "2024", [amount])
        model.write(component, True, "2024", amount, True, "after bulk delete")
        # Add this state after the composition: warming every component
        # beforehand would create unrelated physical formulas whose later
        # deletion clears the memo, masking a lost fast-only return's date.
        # Both invariants still check every state after every generated step.
        self.append(simulation, model)

    @rule(
        slot=TARGET,
        component=COMPONENT,
        reported=st.booleans(),
        period=PERIOD,
        amount=AMOUNT,
        data=st.data(),
    )
    def dataset_load(self, slot, component, reported, period, amount, data=None):
        simulation, model = self.state(slot)
        component, period = self.write_key(model, component, period, data)
        simulation.dataset = self.backend.Dataset(
            {self.name(component, reported): {period: [amount]}}
        )
        simulation.build_from_dataset()
        model = Model(
            branch_name=model.branch_name, visible_branches=model.visible_branches
        )
        model.write(component, reported, period, amount, True, "dataset", initial=True)
        self.states[slot % len(self.states)] = (simulation, model)

    @rule(
        slot=TARGET,
        component=COMPONENT,
        reported=st.booleans(),
        period=PERIOD,
        amount=AMOUNT,
        data=st.data(),
        fresh=st.booleans(),
        yaml=st.booleans(),
    )
    def builder_load(
        self, slot, component, reported, period, amount, fresh, yaml, data=None
    ):
        simulation, model = self.state(slot)
        component, period = self.write_key(model, component, period, data)
        if fresh:
            simulation, model = None, Model()
        name = self.name(component, reported)
        builder = self.backend.Builder()
        if simulation is not None:
            self.prepare_core_input_drop(simulation, model, name, period, amount)
        if yaml:
            # This executes Core build_from_dict -> build_from_entities ->
            # finalize_variables_init -> Holder.set_input, including nested
            # loading contexts and exact multi-year periods.
            inputs = {
                "people": {"person_1": {name: {period: amount}}},
                "households": {"household": {"members": ["person_1"]}},
            }
            result = builder.build_from_dict(
                self.backend.system, inputs, simulation=simulation
            )
        else:
            result = builder.build_from_variables(
                self.backend.system, {name: {period: [amount]}}, simulation=simulation
            )
        if simulation is not None:
            assert result is simulation
        model.write(
            component,
            reported,
            period,
            amount,
            True,
            "yaml" if yaml else "builder",
            initial=True,
            branch_name="default" if yaml else model.branch_name,
            cleanup=self.backend.cleans_raw_overlaps,
        )
        if fresh:
            self.append(result, model)

    @rule(
        slot=TARGET,
        component=COMPONENT,
        reported=st.booleans(),
        period=PERIOD,
        amount=AMOUNT,
        data=st.data(),
        initial=st.booleans(),
    )
    def setter_stores_then_raises(
        self, slot, component, reported, period, amount, initial, data=None
    ):
        simulation, model = self.state(slot)
        component, period = self.write_key(model, component, period, data)
        # A Core-created/restored instance is upgraded only by calling the
        # delegating method explicitly, without replacing any hook.
        original_class = type(simulation)
        simulation.__class__ = self.backend.DelegatingSimulation
        simulation.fail_after_store = True
        simulation.fail_name = self.name(component, reported)
        self.prepare_core_input_drop(
            simulation, model, simulation.fail_name, period, amount
        )
        error = None
        try:
            name = self.name(component, reported)
            if initial:
                self.backend.Builder().build_from_variables(
                    self.backend.system,
                    {name: {period: [amount]}},
                    simulation=simulation,
                )
            else:
                simulation.set_input(name, period, [amount])
        except RuntimeError as caught:
            error = caught
        finally:
            simulation.fail_after_store = False
            simulation.__class__ = original_class
        assert (
            error is not None
            and str(error) == "stored input before intentional setter failure"
        )
        assert error is simulation.last_error
        model.write(
            component,
            reported,
            period,
            amount,
            True,
            "failed initial setter" if initial else "failed setter",
            initial=initial,
            cleanup=self.backend.cleans_raw_overlaps,
        )

    @rule(slot=TARGET, branch=st.booleans())
    def copy_simulation(self, slot, branch):
        simulation, model = self.state(slot)
        copied = (
            simulation.get_branch(f"copy_{len(self.states)}")
            if branch
            else simulation.clone()
        )
        copied_model = copy.deepcopy(model)
        if branch:
            copied_model.branch_name = copied.branch_name
            copied_model.visible_branches = tuple(
                dict.fromkeys((copied.branch_name, *copied_model.visible_branches))
            )
        self.append(copied, copied_model)

    @precondition(lambda self: not self.branch_initial_rewrite_done)
    @rule(
        slot=TARGET,
        component=COMPONENT,
        period=PERIOD,
        amount=AMOUNT,
        replacement=AMOUNT,
    )
    def branch_initial_rewrite(self, slot, component, period, amount, replacement):
        """Compose an inherited final override with a branch's initial rewrite."""
        _, model = self.state(slot)
        if model.visible(model.explicit, component, period) is not None:
            # A same-period explicit twin intentionally retains the public
            # override; this composition exercises initial source routing.
            return
        # Independent rules rarely choose the same component and period on
        # a newly created branch. Keep that composition generated, checking
        # the parent and every earlier copy after each intermediate step.
        # One composed rewrite bounds retained-copy growth; the independent
        # primitive rules can still compose before and after it on any state.
        self.set_input(slot, component, False, period, amount, "simulation")
        self.reported_values_and_provenance_follow_intent()
        self.copy_simulation(slot, branch=True)
        self.reported_values_and_provenance_follow_intent()
        self.builder_load(
            len(self.states) - 1,
            component,
            False,
            period,
            replacement,
            fresh=False,
            yaml=False,
        )
        self.branch_initial_rewrite_done = True

    @rule(slot=TARGET)
    def dump_restore(self, slot):
        simulation, model = self.state(slot)
        directory = Path(self.temp.name) / f"dump_{self.dump_count}"
        self.dump_count += 1
        self.backend.dumper.dump_simulation(simulation, directory)
        restored = self.backend.dumper.restore_simulation(
            directory, self.backend.system
        )
        copied_model = copy.deepcopy(model)
        copied_model.flatten(promote_raw=True)
        self.append(restored, copied_model)

    @rule(slot=TARGET, full_history=st.booleans())
    def extract_reload(self, slot, full_history=False):
        simulation, model = self.state(slot)
        if full_history:
            payload = self.backend.hooks["export_source_inputs"](simulation)
            restored = self.backend.hooks["reload_source_inputs"](
                payload, tax_benefit_system=self.backend.system
            )
        else:
            payload = simulation.extract_person()
            restored = self.backend.Builder().build_from_dict(
                self.backend.system, payload
            )
        copied_model = copy.deepcopy(model)
        copied_model.keep_registered()
        copied_model.flatten()
        self.append(restored, copied_model)

    @rule(slot=TARGET, replay=st.booleans())
    def reform_or_drop(self, slot, replay):
        simulation, model = self.state(slot)
        if replay:

            class IdentityReform:
                def apply(self, system):
                    pass

            simulation.apply_reform(IdentityReform())
        else:
            simulation.drop_computed_arrays()
        # Branches already made are replayed by Core apply_reform too, with
        # their independent snapshots. A plain drop affects only its slot.
        affected = {simulation}
        if replay:
            pending = list(simulation.branches.values())
            while pending:
                branch = pending.pop()
                affected.add(branch)
                pending.extend(branch.branches.values())
        for other, other_model in self.states:
            if other in affected:
                other_model.keep_registered()

    @invariant()
    def reported_values_and_provenance_follow_intent(self):
        for simulation, model in self.states:
            assert simulation._user_input_contexts == []
            assert not hasattr(simulation, "_social_security_automatic_reported_inputs")
            assert (
                float(simulation.calculate("unrelated_formula", as_period("2024"))[0])
                == 77
            )
            for key in model.keys():
                component, period = key
                expected, expected_automatic = model.reported(component, period)
                reported = f"{component}_reported"
                actual = simulation.get_holder(reported).get_array(
                    as_period(period), simulation.branch_name
                )
                if expected is None:
                    assert actual is None or simulation.get_holder(reported).is_derived(
                        as_period(period), simulation.branch_name
                    ), (
                        key,
                        "public source shadowed explicit history",
                    )
                    assert not self.backend.hooks["_is_automatic_reported_input"](
                        simulation, reported, as_period(period)
                    )
                    continue
                assert actual is not None, (key, expected.route, "missing source view")
                assert float(actual[0]) == expected.amount, (
                    key,
                    expected.route,
                    float(actual[0]),
                    expected.amount,
                )
                automatic = self.backend.hooks["_is_automatic_reported_input"](
                    simulation, reported, as_period(period)
                )
                assert automatic == expected_automatic, (
                    key,
                    expected.route,
                    "provenance",
                    automatic,
                )
            for component in COMPONENTS:
                reported_holder = simulation.get_holder(f"{component}_reported")
                for period in reported_holder.get_input_periods(simulation.branch_name):
                    key = (component, str(period))
                    assert model.reported(*key)[0] is not None, (
                        key,
                        "unexplained reported input",
                    )
                holder = simulation.get_holder(component)
                for period in holder.get_input_periods(simulation.branch_name):
                    key = (component, str(period))
                    expected = model.visible(model.overrides, *key)
                    assert expected is not None, (key, "unexpected public override")
                    assert (
                        float(holder.get_array(period, simulation.branch_name)[0])
                        == expected.amount
                    )
                # The source view alone cannot expose stale calculated
                # intermediates. Exercise Core's actual calculation body on
                # the scored years and a later year after every operation.
                for year in ("2023", "2024", "2025", "2026"):
                    expected_amount = model.reader_amount(component, year)
                    actual_reported = simulation.calculate(
                        f"{component}_reported", as_period(year)
                    )
                    assert float(actual_reported[0]) == expected_amount, (
                        component,
                        year,
                        "reported reader",
                        float(actual_reported[0]),
                        expected_amount,
                    )
                    source, source_period, expected_automatic = model.reader_source(
                        component, year
                    )
                    if source is not None:
                        value, automatic = self.backend.hooks["_effective_value"](
                            simulation,
                            f"{component}_reported",
                            as_period(source_period),
                        )
                        assert (
                            value is not None and float(value.array[0]) == source.amount
                        ), (
                            component,
                            year,
                            "selected source",
                            source_period,
                        )
                        assert automatic == expected_automatic, (
                            component,
                            year,
                            "selected source provenance",
                            automatic,
                            expected_automatic,
                        )
                    override = model.visible(model.overrides, component, year)
                    expected_public = (
                        override.amount if override is not None else expected_amount * 2
                    )
                    actual_public = simulation.calculate(component, as_period(year))
                    assert float(actual_public[0]) == expected_public, (
                        component,
                        year,
                        "public reader through base and factor",
                        float(actual_public[0]),
                        expected_public,
                    )
            for component, period in model.keys():
                expected = model.visible(model.overrides, component, period)
                if expected is None:
                    continue
                actual = simulation.get_holder(component).get_array(
                    as_period(period), simulation.branch_name
                )
                assert actual is not None and float(actual[0]) == expected.amount, (
                    (component, period),
                    expected.route,
                    "lost public override",
                )


TestSocialSecurityInputStateMachine = SocialSecurityInputsMachine.TestCase
TestSocialSecurityInputStateMachine.settings = settings(
    max_examples=60,
    stateful_step_count=25,
    deadline=None,
    derandomize=True,
    report_multiple_bugs=False,
    suppress_health_check=(HealthCheck.too_slow,),
)


if __name__ == "__main__":
    unittest.main()
