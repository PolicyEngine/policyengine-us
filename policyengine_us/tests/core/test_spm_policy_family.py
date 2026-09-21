"""Policy sharing boundaries a reform, a clone or a prepared system must respect.

These cases come from #9448, which proposed a different isolation mechanism from
the one this branch carries (#9463's). Most of that file asserted #9448's own
internals, or asserted that a child branch's reform propagates up to its parent
and siblings.

#9463 reverses that propagation for parameter reforms only.
``test_a_branch_reform_does_not_rewrite_its_parents_policy`` in
``test_spm_simulation_isolation.py`` pins the reversal; a variable-only reform on
a shared-policy branch still reaches its parent and siblings, and
``test_a_branch_variable_reform_is_not_isolated_from_its_parent`` pins that
retained behaviour. Every propagation case dropped from #9448 carried a
parameter reform - ``test_child_reform_updates_warm_parent_and_sibling``
parametrizes a parameter dictionary against a root-replacing
``modify_parameters`` reform, and
``test_parameter_reform_updates_only_intentionally_shared_branches`` is a
parameter reform by name - so each of them is contradicted rather than merely
duplicated.

What is kept here is the part that is mechanism-independent and that #9463's own
suite leaves uncovered: a nested branch clone's inherited inputs, a structural
reform at a changed start instant, the warm-cache contract for a system supplied
by a caller, and a reform reading back its own in-progress edit.
"""

import importlib

import numpy as np
import pytest
from policyengine_core.parameters import ParameterNode
from policyengine_core.reforms import Reform

from policyengine_us import CountryTaxBenefitSystem, Simulation
from policyengine_us.system import system


def earning_household():
    return {
        "people": {
            "person": {
                "age": {2024: 40},
                "employment_income": {2024: 50_000},
            }
        },
        "households": {
            "household": {
                "members": ["person"],
                "county_fips": {2024: "06037"},
            }
        },
    }


class ReplaceParameterRoot(Reform):
    def apply(self):
        def replace(parameters):
            parameters = parameters.clone()
            parameters.gov.irs.deductions.standard.amount.SINGLE.update(
                period="2024", value=100_000
            )
            # A public modifier may return an ordinary core root, without the
            # country adapter's per-simulation root subclass.
            parameters.__class__ = ParameterNode
            return parameters

        self.modify_parameters(replace)


class VariableOnlyReform(Reform):
    def apply(self):
        self.neutralize_variable("income_tax")


@pytest.mark.parametrize("replace_root", [False, True])
def test_detached_branch_clone_preserves_inherited_inputs_and_private_reform(
    replace_root,
):
    original = Simulation(situation=earning_household())
    middle = original.get_branch("middle")
    middle.set_input("employment_income_before_lsr", 2024, [70_000])
    leaf = middle.get_branch("leaf")
    before = [
        member.calculate("income_tax", 2024).copy()
        for member in (original, middle, leaf)
    ]
    detached = leaf.clone()
    detached.calculate("income_tax", 2024)
    reform = (
        ReplaceParameterRoot
        if replace_root
        else {"gov.irs.deductions.standard.amount.SINGLE": {"2024": 100_000}}
    )
    detached.apply_reform(reform)
    reference_inputs = earning_household()
    reference_inputs["people"]["person"]["employment_income"] = {2024: 70_000}
    reference = Simulation(situation=reference_inputs, reform=reform)
    assert detached.calculate("employment_income", 2024)[0] == 70_000
    np.testing.assert_array_equal(
        detached.calculate("income_tax", 2024), reference.calculate("income_tax", 2024)
    )
    for member, expected in zip((original, middle, leaf), before):
        np.testing.assert_array_equal(member.calculate("income_tax", 2024), expected)


@pytest.mark.parametrize("use_modifier", [False, True])
def test_changed_structural_start_detaches_before_parameter_mutation(
    monkeypatch, use_modifier
):
    module = importlib.import_module("policyengine_us.system")
    source = system.parameters
    children = source.children
    before = source("2024-01-01").gov.irs.deductions.standard.amount.SINGLE
    cached = dict(source.gov._at_instant_cache)

    def mutate(parameters):
        assert parameters.children is not children
        parameters.gov.irs.deductions.standard.amount.SINGLE.update(
            period="2024", value=100_000
        )
        return parameters

    class StructuralParameterChange(Reform):
        def apply(self):
            if use_modifier:
                self.modify_parameters(mutate)
            else:
                mutate(self.parameters)

    monkeypatch.setattr(
        module,
        "create_structural_reforms_from_parameters",
        lambda parameters, instant: StructuralParameterChange,
    )
    simulation = Simulation(situation=earning_household(), start_instant="2026-01-01")
    assert (
        simulation.tax_benefit_system.parameters.gov.irs.deductions.standard.amount.SINGLE(
            2024
        )
        == 100_000
    )
    assert source.gov.irs.deductions.standard.amount.SINGLE(2024) == before
    assert source.children is children
    for instant, node in cached.items():
        assert source.gov._at_instant_cache[instant] is node


@pytest.mark.parametrize(
    "clone_count,reform_wrapper",
    [(0, False), (1, False), (2, False), (0, True), (1, True)],
)
def test_supplied_prepared_system_retains_warm_policy_children(
    clone_count, reform_wrapper
):
    source = CountryTaxBenefitSystem() if not clone_count else system
    for _ in range(clone_count):
        source = source.clone()
    if reform_wrapper:
        source = VariableOnlyReform(source)
    source.parameters("2024-01-01").gov.irs.deductions.standard.amount.SINGLE
    cached = dict(source.parameters.gov._at_instant_cache)
    children = source.parameters.children
    simulation = Simulation(tax_benefit_system=source, situation=earning_household())
    assert simulation.tax_benefit_system.parameters.children is children
    assert source.parameters.gov._at_instant_cache
    for instant, node in cached.items():
        assert (
            simulation.tax_benefit_system.parameters.gov._at_instant_cache[instant]
            is node
        )


def test_a_systems_parameter_view_refreshes_after_an_in_place_leaf_update():
    """An at-instant read taken before an in-place edit must not be served again."""
    source = system.clone()
    assert (
        source.parameters("2024-01-01").gov.irs.deductions.standard.amount.SINGLE
        < 100_000
    )
    source.parameters.gov.irs.deductions.standard.amount.SINGLE.update(
        period="2024", value=100_000
    )
    assert (
        source.parameters("2024-01-01").gov.irs.deductions.standard.amount.SINGLE
        == 100_000
    )


def test_reform_can_read_updated_parameters_before_returning():
    class ReadDuringUpdate(Reform):
        def apply(self):
            parameters = self.parameters
            assert (
                parameters("2024-01-01").gov.irs.deductions.standard.amount.SINGLE
                < 100_000
            )
            parameters.gov.irs.deductions.standard.amount.SINGLE.update(
                period="2024", value=100_000
            )
            assert (
                parameters("2024-01-01").gov.irs.deductions.standard.amount.SINGLE
                == 100_000
            )

    simulation = Simulation(situation=earning_household())
    simulation.apply_reform(ReadDuringUpdate)
