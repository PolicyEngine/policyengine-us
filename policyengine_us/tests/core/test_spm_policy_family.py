"""Reforms and tracing must respect intentional policy sharing boundaries."""

import importlib

import numpy as np
import pytest
from policyengine_core.reforms import Reform
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import period
from policyengine_core.tracers import FullTracer

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


@pytest.mark.parametrize("replace_root", [False, True])
def test_child_reform_updates_warm_parent_and_sibling(replace_root):
    parent = Simulation(situation=earning_household())
    child = parent.get_branch("child")
    sibling = parent.get_branch("sibling")
    independent = parent.get_branch("independent", clone_system=True)
    for member in (parent, child, sibling, independent):
        assert member.calculate("income_tax", 2024)[0] > 0
    independent_before = independent.calculate("income_tax", 2024).copy()
    reform = (
        ReplaceParameterRoot
        if replace_root
        else {"gov.irs.deductions.standard.amount.SINGLE": {"2024": 100_000}}
    )
    child.apply_reform(reform)
    expected = Simulation(situation=earning_household(), reform=reform).calculate(
        "income_tax", 2024
    )
    assert expected[0] < independent_before[0]
    for member in (parent, child, sibling):
        np.testing.assert_array_equal(member.calculate("income_tax", 2024), expected)
        assert member.calculate("employment_income", 2024)[0] == 50_000
    np.testing.assert_array_equal(
        independent.calculate("income_tax", 2024), independent_before
    )


def test_cached_formula_trace_binds_replacement_tracer():
    simulation = Simulation(situation=earning_household(), trace=True)
    simulation.calculate("spm_unit_fpg", 2024)
    old_tracer = simulation.tracer
    old_count = len(old_tracer.trees)
    simulation.tracer = FullTracer()
    simulation.calculate("spm_unit_fpg", 2024)
    assert any(
        parameter.name.endswith("gov.abolitions.spm_unit_fpg")
        for parameter in simulation.tracer.trees[-1].parameters
    )
    assert len(old_tracer.trees) == old_count


def test_constructor_replaced_root_keeps_tracing_private():
    simulation = Simulation(
        situation=earning_household(), reform=ReplaceParameterRoot, trace=True
    )
    simulation.calculate("spm_unit_fpg", 2024)
    first_tracer = simulation.tracer
    simulation.tracer = FullTracer()
    simulation.delete_arrays("spm_unit_fpg")
    simulation.calculate("spm_unit_fpg", 2024)
    assert simulation.tracer.trees[-1].parameters
    assert len(first_tracer.trees) == 1


def test_system_parameter_lookup_does_not_cache_tracer():
    source = system.clone()
    source.parameters.trace = True
    source.parameters.branch_name = "default"
    tracers = [FullTracer(), FullTracer()]
    for tracer in tracers:
        source.parameters.tracer = tracer
        tracer.record_calculation_start("probe", period(2024), "default")
        value = source.get_parameters_at_instant(
            2024
        ).gov.irs.deductions.standard.amount.SINGLE
        tracer.record_calculation_result(np.array([value]))
        tracer.record_calculation_end()
        assert len(tracer.trees[-1].parameters) == 1
    assert len(tracers[0].trees[-1].parameters) == 1


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


def test_explicit_shared_clones_participate_without_branch_registration():
    original = Simulation(situation=earning_household())
    first = original.clone(clone_tax_benefit_system=False)
    second = original.clone(clone_tax_benefit_system=False)
    for owner in (original, first, second):
        owner.calculate("income_tax", 2024)
    first.apply_reform(ReplaceParameterRoot)
    reference = Simulation(situation=earning_household(), reform=ReplaceParameterRoot)
    expected = reference.calculate("income_tax", 2024)
    for owner in (original, first, second):
        np.testing.assert_array_equal(owner.calculate("income_tax", 2024), expected)


def test_reusing_detached_source_marks_all_shared_owners_for_copy_on_write():
    from policyengine_us.spm import share_spm_policy

    original = Simulation(situation=earning_household()).clone()
    sibling = original.get_branch("sibling")
    separate = share_spm_policy(original.tax_benefit_system)
    before = separate.parameters.gov.irs.deductions.standard.amount.SINGLE(2024)
    sibling.apply_reform(
        {"gov.irs.deductions.standard.amount.SINGLE": {"2024": 100_000}}
    )
    assert separate.parameters.gov.irs.deductions.standard.amount.SINGLE(2024) == before
    for owner in (original, sibling):
        assert (
            owner.tax_benefit_system.parameters.gov.irs.deductions.standard.amount.SINGLE(
                2024
            )
            == 100_000
        )


def test_modified_replacement_default_applies_new_structure(monkeypatch):
    source = system.clone()
    source.parameters.gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax.update(
        period="2024", value=True
    )
    baseline = Simulation(situation=earning_household())
    before = baseline.calculate("household_tax_before_refundable_credits", 2024)
    explicit = Simulation(tax_benefit_system=source, situation=earning_household())
    expected = explicit.calculate("household_tax_before_refundable_credits", 2024)
    assert expected[0] < before[0]
    monkeypatch.setattr(Simulation, "default_tax_benefit_system_instance", source)
    simulation = Simulation(situation=earning_household())
    np.testing.assert_allclose(
        simulation.calculate("household_tax_before_refundable_credits", 2024),
        expected,
    )


@pytest.mark.parametrize("start_instant", ["2024-01-01", "2026-01-01"])
def test_structural_detection_reuses_only_matching_default(monkeypatch, start_instant):
    module = importlib.import_module("policyengine_us.system")
    calls = []
    original = module.create_structural_reforms_from_parameters

    def record(parameters, instant):
        calls.append(instant)
        return original(parameters, instant)

    monkeypatch.setattr(module, "create_structural_reforms_from_parameters", record)
    Simulation(situation=earning_household(), start_instant=start_instant)
    assert calls == ([] if start_instant == "2024-01-01" else [start_instant])


def test_supplied_prepared_system_retains_warm_policy_children():
    source = CountryTaxBenefitSystem()
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


def test_parameter_view_refreshes_after_in_place_leaf_update():
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
