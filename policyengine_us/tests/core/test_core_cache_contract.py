"""Exercise US adapters with a three-variable policy, not repeated US builds.

These are engineering contracts: YAML cannot express array ownership, changing
a supplied input after calculation, shared policy identity, or trace ownership.
The existing SPM modules cover the same interfaces with the full US model.
"""

import ast
from pathlib import Path

import numpy as np
import pytest
from policyengine_core.entities import Entity
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import YEAR, period
from policyengine_core.reforms import Reform
from policyengine_core.simulations import Simulation as CoreSimulation
from policyengine_core.taxbenefitsystems import TaxBenefitSystem
from policyengine_core.variables import Variable

from policyengine_us.spm import (
    SPMSimulationMixin,
    clone_spm_system,
    with_parameter_barrier,
)
from policyengine_us.tools.period_branch import (
    get_branch_for_period,
    get_override_branch,
)

PERSON = Entity("person", "people", "Person", "Minimal test population")


class source_value(Variable):
    label = "Synthetic supplied value"
    value_type = float
    entity = PERSON
    definition_period = YEAR


class retained_input(Variable):
    label = "Independent supplied value"
    value_type = float
    entity = PERSON
    definition_period = YEAR


class derived_value(Variable):
    label = "Synthetic parameter-dependent result"
    value_type = float
    entity = PERSON
    definition_period = YEAR

    def formula(person, period, parameters):
        return person("source_value", period) * parameters(period).multiplier


class EmptyProvider:
    """Do not load forecast data when only the adapter lifecycle is tested."""

    def snapshot(self, *, copy_receipts=False):
        return type(self)()


class MinimalSystem(TaxBenefitSystem):
    def __init__(self):
        super().__init__([PERSON])
        self.add_variables(source_value, retained_input, derived_value)
        self.replace_parameters(
            ParameterNode(
                "test_policy", data={"multiplier": {"values": {"2020-01-01": 2}}}
            )
        )
        self.spm_forecast_provider = EmptyProvider()

    def clone(self):
        return clone_spm_system(self)


class MinimalSimulation(SPMSimulationMixin, CoreSimulation):
    default_tax_benefit_system = MinimalSystem


@pytest.fixture
def simulation():
    return MinimalSimulation(
        tax_benefit_system=with_parameter_barrier(MinimalSystem()),
        situation={
            "people": {
                "person": {
                    "source_value": {2024: 10, 2025: 20},
                    "retained_input": {2024: 7},
                }
            }
        },
    )


@pytest.mark.parametrize("value", [0, -5, 30])
@pytest.mark.parametrize("warm_parent", [False, True])
def test_override_uses_core_invalidation_without_country_storage_edits(
    simulation, value, warm_parent
):
    if warm_parent:
        assert simulation.calculate("derived_value", 2024)[0] == 20
    branch = get_override_branch(
        simulation, "comparison", period(2024), {"source_value": [value]}
    )

    assert branch.calculate("derived_value", 2024)[0] == value * 2
    assert branch.get_supplied_input("retained_input", 2024)[0] == 7
    assert simulation.calculate("derived_value", 2024)[0] == 20


@pytest.mark.parametrize("depth", [1, 2])
@pytest.mark.parametrize("write_through_holder", [False, True])
def test_parent_input_change_does_not_clear_us_branch_snapshot(
    simulation, depth, write_through_holder
):
    branch = simulation
    for index in range(depth):
        branch = branch.get_branch(f"level_{index}")
    cached = branch.calculate("derived_value", 2024)

    if write_through_holder:
        simulation.get_holder("source_value").set_input(2024, [30])
    else:
        simulation.set_input("source_value", 2024, [30])

    assert simulation.calculate("derived_value", 2024)[0] == 60
    assert branch.get_array("derived_value", 2024) is not None
    np.testing.assert_array_equal(branch.calculate("derived_value", 2024), cached)
    assert branch.get_supplied_input("source_value", 2024)[0] == 10


class DoubleMultiplier(Reform):
    def apply(self):
        self.modify_parameters({"multiplier": {"2024": 4}})


class ReplaceMultiplierRoot(Reform):
    def apply(self):
        def replace(parameters):
            replaced = parameters.clone()
            replaced.multiplier.update(period="2024", value=4)
            return replaced

        self.modify_parameters(replace)


@pytest.mark.parametrize("reform", [DoubleMultiplier, ReplaceMultiplierRoot])
def test_parameter_adoption_invalidates_only_linked_policy_results(simulation, reform):
    child = simulation.get_branch("child")
    leaf = child.get_branch("leaf")
    independent = simulation.get_branch("independent", clone_system=True)
    for member in (simulation, child, leaf, independent):
        assert member.calculate("derived_value", 2024)[0] == 20

    simulation.apply_reform(reform)

    for member in (simulation, child, leaf):
        assert member.calculate("derived_value", 2024)[0] == 40
    assert independent.calculate("derived_value", 2024)[0] == 20
    assert independent.tax_benefit_system.parameters.multiplier(2024) == 2


def test_baseline_snapshot_keeps_unreformed_results_and_inputs(simulation):
    baseline = simulation.get_branch("baseline", clone_system=True)
    assert baseline.calculate("derived_value", 2024)[0] == 20

    simulation.apply_reform(DoubleMultiplier)
    simulation.set_input("source_value", 2024, [30])

    assert simulation.calculate("derived_value", 2024)[0] == 120
    assert baseline.calculate("derived_value", 2024)[0] == 20
    assert baseline.get_supplied_input("source_value", 2024)[0] == 10


class NeutralizeDerived(Reform):
    def apply(self):
        self.neutralize_variable("derived_value")


def test_variable_only_reform_keeps_shared_parameters_and_warm_views(simulation):
    simulation.get_branch("child")
    policy = simulation.tax_benefit_system
    shared_parameters = policy.parameters
    cached_view = policy.get_parameters_at_instant("2024-01-01")

    simulation.apply_reform(NeutralizeDerived)

    assert policy.parameters is shared_parameters
    assert policy.get_parameters_at_instant("2024-01-01") is cached_view
    assert simulation.calculate("derived_value", 2024)[0] == 0


@pytest.mark.parametrize("reform_on_child", [False, True])
def test_shared_variable_reform_refreshes_warm_family_but_not_private_policy(
    simulation, reform_on_child
):
    child = simulation.get_branch("child")
    sibling = simulation.get_branch("sibling")
    independent = simulation.get_branch("independent", clone_system=True)
    for member in (simulation, child, sibling, independent):
        assert member.calculate("derived_value", 2024)[0] == 20

    (child if reform_on_child else simulation).apply_reform(NeutralizeDerived)

    for member in (simulation, child, sibling):
        assert member.calculate("derived_value", 2024)[0] == 0
    assert independent.calculate("derived_value", 2024)[0] == 20


def test_period_branch_without_overrides_keeps_inherited_results(simulation):
    cached = simulation.calculate("derived_value", 2024)
    branch = get_branch_for_period(simulation, "comparison", period(2024))
    assert branch.get_array("derived_value", 2024) is not None
    np.testing.assert_array_equal(branch.calculate("derived_value", 2024), cached)


def test_same_period_and_inputs_reuse_branch(simulation):
    original = get_override_branch(
        simulation, "comparison", period(2024), {"source_value": [30]}
    )
    assert (
        get_override_branch(
            simulation, "comparison", period(2024), {"source_value": [30]}
        )
        is original
    )


@pytest.mark.parametrize(
    "mutation", ["simulation", "holder", "delete", "holder_delete", "retain"]
)
def test_formula_branch_refreshes_after_parent_supplied_inputs_change(
    simulation, mutation
):
    inputs = {"retained_input": [9]}
    original = get_override_branch(simulation, "comparison", period(2024), inputs)
    assert original.calculate("derived_value", 2024)[0] == 20

    if mutation == "simulation":
        simulation.set_input("source_value", 2024, [30])
    elif mutation == "holder":
        simulation.get_holder("source_value").set_input(2024, [30])
    elif mutation == "delete":
        simulation.delete_arrays("source_value", 2024)
    elif mutation == "holder_delete":
        simulation.get_holder("source_value").delete_arrays(period(2024))
    else:
        simulation.retain_supplied_inputs(["retained_input"])
    refreshed = get_override_branch(simulation, "comparison", period(2024), inputs)

    assert refreshed is not original
    assert refreshed.calculate("derived_value", 2024)[0] == (
        60 if mutation in ("simulation", "holder") else 0
    )
    # The old branch remains a valid independent input snapshot.
    assert original.calculate("derived_value", 2024)[0] == 20


def test_clearing_parent_results_does_not_replace_formula_branch(simulation):
    inputs = {"retained_input": [9]}
    original = get_override_branch(simulation, "comparison", period(2024), inputs)
    simulation.calculate("derived_value", 2024)
    simulation.clear_calculated_results()

    assert (
        get_override_branch(simulation, "comparison", period(2024), inputs) is original
    )


@pytest.mark.parametrize(
    "new_period, inputs",
    [(2025, {"source_value": [30]}), (2024, {"source_value": [40]})],
)
def test_new_period_or_inputs_replace_branch(simulation, new_period, inputs):
    original = get_override_branch(
        simulation, "comparison", period(2024), {"source_value": [30]}
    )
    replacement = get_override_branch(
        simulation, "comparison", period(new_period), inputs
    )
    assert replacement is not original
    assert replacement.calculate("derived_value", new_period)[0] == (
        inputs["source_value"][0] * 2
    )


@pytest.mark.parametrize("explicit_period", [False, True])
def test_mutating_caller_override_does_not_mutate_branch_reuse_key(
    simulation, explicit_period
):
    value = np.array([30.0])
    inputs = {"source_value": (period(2024), value) if explicit_period else value}
    original = get_override_branch(simulation, "comparison", period(2024), inputs)
    value[0] = 40

    replacement = get_override_branch(simulation, "comparison", period(2024), inputs)

    assert replacement is not original
    assert original.calculate("derived_value", 2024)[0] == 60
    assert replacement.calculate("derived_value", 2024)[0] == 80


@pytest.mark.parametrize("make_writeable", [False, True])
def test_override_comparison_snapshot_rejects_mutation(simulation, make_writeable):
    branch = get_override_branch(
        simulation, "comparison", period(2024), {"source_value": [30]}
    )
    value = branch.branch_overrides[0][2]
    with pytest.raises(ValueError):
        if make_writeable:
            value.setflags(write=True)
        else:
            value[0] = 40
    assert branch.calculate("derived_value", 2024)[0] == 60


def test_override_on_current_branch_uses_core_invalidation(simulation):
    branch = simulation.get_branch("comparison")
    branch.calculate("derived_value", 2024)
    assert (
        get_override_branch(branch, "comparison", period(2024), {"source_value": [30]})
        is branch
    )
    assert branch.calculate("derived_value", 2024)[0] == 60


@pytest.mark.parametrize("alias", ["calc", "custom_calculation"])
def test_us_clone_uses_core_alias_rebinding(simulation, alias):
    simulation.custom_calculation = simulation.calculate
    cloned = simulation.clone()
    cloned.set_input("source_value", 2024, [30])
    assert getattr(cloned, alias).__self__ is cloned
    assert getattr(cloned, alias)("derived_value", 2024)[0] == 60
    assert simulation.calculate("derived_value", 2024)[0] == 20


@pytest.mark.parametrize("write_through_holder", [False, True])
def test_deleting_us_branch_input_keeps_provenance_consistent(
    simulation, write_through_holder
):
    branch = simulation.get_branch("comparison")
    branch.set_input("source_value", 2024, [30])
    if write_through_holder:
        branch.get_holder("source_value").delete_arrays(
            period(2024), branch_name=branch.branch_name
        )
    else:
        branch.delete_arrays("source_value", 2024)
    remaining = branch.get_supplied_input("source_value", 2024)
    if write_through_holder:
        # The copied parent input remains visible after removing just the
        # branch override, and its provenance must remain with it.
        assert remaining[0] == 10
        assert branch.supplied_input_periods("source_value") == [
            period(2024),
            period(2025),
        ]
    else:
        assert remaining is None
        assert branch.supplied_input_periods("source_value") == [period(2025)]
    assert simulation.get_supplied_input("source_value", 2024)[0] == 10


@pytest.mark.parametrize("trace_parent", [False, True])
def test_traced_us_branch_keeps_parameter_records_local(simulation, trace_parent):
    simulation.trace = trace_parent
    branch = simulation.get_branch("comparison")
    branch.trace = True
    branch.clear_calculated_results()
    branch.calculate("derived_value", 2024)
    assert any(
        parameter.name == "test_policy.multiplier"
        for node in branch.tracer.trees
        for parameter in node.parameters
    )
    if trace_parent:
        assert simulation.tracer.trees == []


def test_production_does_not_use_core_cache_backing_collections():
    root = Path(__file__).resolve().parents[2]
    forbidden = {
        "_at_instant_cache",
        "_parameters_at_instant_cache",
        "_user_input_keys",
        "_user_input_contexts",
        "_fast_cache",
        "_memory_storage",
        "_disk_storage",
        "invalidated_caches",
        "replace_supplied_inputs",
        "_invalidate_all_caches",
    }
    violations = []
    for path in root.rglob("*.py"):
        if "tests" in path.relative_to(root).parts:
            continue
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Attribute) and node.attr in forbidden:
                violations.append(f"{path.relative_to(root)}:{node.lineno}:{node.attr}")
    assert violations == []
