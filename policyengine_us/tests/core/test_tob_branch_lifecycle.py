"""Counterfactual branches retain only their returned income-tax array."""

from types import SimpleNamespace
import weakref

import numpy as np
import pytest

from policyengine_us.tools import tob


class FakeBranch:
    def __init__(self, parent):
        self.parent = parent
        self.cycle = self
        self.tax_benefit_system = SimpleNamespace(
            neutralize_variable=lambda name: parent.events.append(("neutralize", name))
        )

    def get_holder(self, name):
        assert name == "tax_unit_taxable_social_security"
        return self

    def set_input(self, period, values):
        self.parent.events.append(("input", period, tuple(values)))

    def tax_unit(self, name, period):
        self.parent.events.append(("calculate", name, period))
        if self.parent.fail:
            raise RuntimeError("counterfactual failed")
        return self.parent.result


class FakeSimulation:
    def __init__(self, *, fail=False):
        self.events = []
        self.branches = {}
        self.references = []
        self.result = np.array([-2.0, 17.0], dtype=np.float32)
        self.fail = fail

    def get_branch(self, name, clone_system):
        assert clone_system
        assert not self.branches
        # Population/holder cycles must be collected before another branch.
        assert all(reference() is None for reference in self.references)
        branch = FakeBranch(self)
        self.branches[name] = branch
        self.references.append(weakref.ref(branch))
        return branch


@pytest.mark.parametrize("override", [None, np.array([30.0, 40.0])])
def test_counterfactual_releases_branch_and_copies_result(monkeypatch, override):
    simulation = FakeSimulation()
    monkeypatch.setattr(
        tob,
        "drop_inherited_values",
        lambda branch: branch.parent.events.append(("drop",)),
    )

    result = tob.income_tax_with_social_security_override(
        simulation, 2026, taxable_social_security=override
    )

    np.testing.assert_array_equal(result, [-2.0, 17.0])
    assert not np.shares_memory(result, simulation.result)
    assert not simulation.branches
    assert simulation.references[0]() is None
    setup = (
        [("neutralize", "tax_unit_taxable_social_security"), ("drop",)]
        if override is None
        else [("drop",), ("input", 2026, tuple(override))]
    )
    assert simulation.events == setup + [("calculate", "income_tax", 2026)]


def test_counterfactuals_are_released_before_next_branch(monkeypatch):
    simulation = FakeSimulation()
    monkeypatch.setattr(tob, "drop_inherited_values", lambda branch: None)

    tob.income_tax_with_social_security_override(simulation, 2026)
    tob.income_tax_with_social_security_override(
        simulation, 2026, taxable_social_security=np.array([30.0, 40.0])
    )

    assert len(simulation.references) == 2
    assert all(reference() is None for reference in simulation.references)


def test_failed_counterfactual_is_removed(monkeypatch):
    simulation = FakeSimulation(fail=True)
    monkeypatch.setattr(tob, "drop_inherited_values", lambda branch: None)

    with pytest.raises(RuntimeError, match="counterfactual failed"):
        tob.income_tax_with_social_security_override(simulation, 2026)

    assert not simulation.branches


NO_SS = "income_tax_without_social_security"
OLD_LAW = "income_tax_with_pre_1993_social_security"
OASDI = "tob_revenue_oasdi"
HI = "tob_revenue_medicare_hi"
TOTAL = "tob_revenue_total"


class FakeCalculationBase:
    default_calculation_period = 2026

    def __init__(self, *, cached=(), neutralized=(), custom=()):
        self.cached = set(cached)
        self.neutralized = set(neutralized)
        self.custom = set(custom)
        self.events = []

    def get_holder(self, name):
        return SimpleNamespace(
            variable=SimpleNamespace(is_neutralized=name in self.neutralized)
        )

    def get_array(self, name, period):
        return np.array([1.0]) if name in self.cached else None

    def calculate(self, name, period=None, *args, **kwargs):
        self.events.append(("calculate", name, period, args, kwargs))
        self.cached.add(name)
        return name


class FakeTobCalculation(tob.TobCalculationMixin, FakeCalculationBase):
    def _uses_standard_tob_formula(self, name, period):
        return name not in self.custom


def _record_collection(monkeypatch, simulation):
    monkeypatch.setattr(
        tob.gc, "collect", lambda: simulation.events.append(("collect",))
    )


@pytest.mark.parametrize(
    "requested, states",
    [(OASDI, [NO_SS, OLD_LAW]), (HI, [NO_SS, OLD_LAW]), (TOTAL, [NO_SS])],
)
def test_tob_states_finish_before_requested_calculation(monkeypatch, requested, states):
    simulation = FakeTobCalculation()
    _record_collection(monkeypatch, simulation)

    result = simulation.calculate(requested, 2026)

    expected = []
    for state in states:
        expected.extend([("calculate", state, 2026, (), {}), ("collect",)])
    assert simulation.events == expected + [("calculate", requested, 2026, (), {})]
    assert result == requested


@pytest.mark.parametrize("available", ["cached", "neutralized", "custom"])
def test_tob_prefetch_preserves_available_or_replaced_target(monkeypatch, available):
    # Supplied inputs and previously computed outputs both appear as cached
    # arrays. Neutralized and reform-provided formulas also need no warmup.
    simulation = FakeTobCalculation(**{available: [OASDI]})
    _record_collection(monkeypatch, simulation)

    simulation.calculate(OASDI, 2026)

    assert simulation.events == [("calculate", OASDI, 2026, (), {})]


@pytest.mark.parametrize(
    "cached, states",
    [([TOTAL], [NO_SS, OLD_LAW]), ([OASDI], [NO_SS]), ([TOTAL, OASDI], [])],
)
def test_hi_only_prefetches_missing_allocation_dependencies(
    monkeypatch, cached, states
):
    simulation = FakeTobCalculation(cached=cached)
    _record_collection(monkeypatch, simulation)

    simulation.calculate(HI, 2026)

    calculated = [event[1] for event in simulation.events if event[0] == "calculate"]
    assert calculated == states + [HI]


def test_tob_reuses_states_and_forwards_original_request_options(monkeypatch):
    simulation = FakeTobCalculation(cached=[NO_SS])
    _record_collection(monkeypatch, simulation)

    simulation.calculate(OASDI, None, "person", decode_enums=False)

    assert simulation.events == [
        ("calculate", OLD_LAW, 2026, (), {}),
        ("collect",),
        ("calculate", OASDI, None, ("person",), {"decode_enums": False}),
    ]
