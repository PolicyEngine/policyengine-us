"""Search compositions of public and reported Social Security input routes.

Property: for every component and exact supplied period, an explicit reported
input has priority; otherwise the reported value follows the latest public
input, with automatic provenance. Copies preserve that property and public
final overrides, while subsequent writes remain isolated from their source.

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
    # These dictionaries describe caller intent, never inspect production
    # provenance to decide whether a twin is automatic or explicit.
    public: dict = field(default_factory=dict)
    explicit: dict = field(default_factory=dict)
    overrides: dict = field(default_factory=dict)

    def write(
        self, component, reported, period, amount, registered, route, initial=False
    ):
        key = (component, period)
        value = Input(amount, registered, route)
        if reported:
            self.explicit[key] = value
        else:
            self.public[key] = value
            if initial and key not in self.explicit:
                self.overrides.pop(key, None)
            else:
                self.overrides[key] = value

    def keep_registered(self):
        self.public = {
            key: value for key, value in self.public.items() if value.registered
        }
        self.explicit = {
            key: value for key, value in self.explicit.items() if value.registered
        }
        self.overrides = {
            key: value for key, value in self.overrides.items() if value.registered
        }

    def dump_promotes_raw(self):
        for mapping in (self.public, self.explicit, self.overrides):
            for value in mapping.values():
                value.registered = True


class SocialSecurityInputsMachine(RuleBasedStateMachine):
    """All writes may slot earlier clones, branches, or restored copies."""

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
        keys = sorted(model.public.keys() | model.explicit.keys())
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
        model.write(component, reported, period, amount, True, route)

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
        simulation.get_holder(self.name(component, reported)).put_in_cache(
            [amount], as_period(period), simulation.branch_name, derived=True
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
        model = Model()
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
        )

    @rule(slot=TARGET, branch=st.booleans())
    def copy_simulation(self, slot, branch):
        simulation, model = self.state(slot)
        copied = (
            simulation.get_branch(f"copy_{len(self.states)}")
            if branch
            else simulation.clone()
        )
        self.append(copied, copy.deepcopy(model))

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
        copied_model.dump_promotes_raw()
        self.append(restored, copied_model)

    @rule(slot=TARGET)
    def extract_reload(self, slot):
        simulation, model = self.state(slot)
        payload = simulation.extract_person()
        restored = self.backend.Builder().build_from_dict(self.backend.system, payload)
        copied_model = copy.deepcopy(model)
        copied_model.keep_registered()
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
            for key in model.public.keys() | model.explicit.keys():
                component, period = key
                expected = model.explicit.get(key, model.public.get(key))
                reported = f"{component}_reported"
                actual = simulation.get_holder(reported).get_array(
                    as_period(period), simulation.branch_name
                )
                assert actual is not None, (key, expected.route, "missing twin")
                assert float(actual[0]) == expected.amount, (
                    key,
                    expected.route,
                    float(actual[0]),
                    expected.amount,
                )
                automatic = self.backend.hooks["_is_automatic_reported_input"](
                    simulation, reported, as_period(period)
                )
                assert automatic == (key not in model.explicit), (
                    key,
                    expected.route,
                    "provenance",
                    automatic,
                )
            for component in COMPONENTS:
                reported_holder = simulation.get_holder(f"{component}_reported")
                for period in reported_holder.get_input_periods(simulation.branch_name):
                    key = (component, str(period))
                    assert key in model.public or key in model.explicit, (
                        key,
                        "unexplained reported input",
                    )
                holder = simulation.get_holder(component)
                for period in holder.get_input_periods(simulation.branch_name):
                    key = (component, str(period))
                    expected = model.overrides.get(key)
                    assert expected is not None, (key, "unexpected public override")
                    assert (
                        float(holder.get_array(period, simulation.branch_name)[0])
                        == expected.amount
                    )
            for (component, period), expected in model.overrides.items():
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
