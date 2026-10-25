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
from hypothesis.stateful import RuleBasedStateMachine, invariant, rule


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
        self.backend = Backend()
        self.states = [(self.backend.DelegatingSimulation(), Model())]
        self.temp = tempfile.TemporaryDirectory(prefix="ss-input-machine-")
        self.dump_count = 0

    def teardown(self):
        self.temp.cleanup()
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
        simulation.get_holder(self.name(component, reported)).put_in_cache(
            [amount], as_period(period), simulation.branch_name, derived=False
        )
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
