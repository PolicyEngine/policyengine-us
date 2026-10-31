"""Sequential TOB counterfactuals equal the original signed main formulas."""

import gc
import weakref

import numpy as np

from policyengine_us.tests.microsimulation.test_calculate_chunked import (
    YEAR,
    build_chunking_dataset,
    make_simulation,
)


def _main_counterfactual(simulation, name, taxable_social_security=None):
    """Reproduce main's branch algorithm independently of the new helper."""
    branch = simulation.get_branch(name, clone_system=True)
    try:
        if taxable_social_security is None:
            branch.tax_benefit_system.neutralize_variable(
                "tax_unit_taxable_social_security"
            )
        input_variables = set(branch.input_variables)
        for variable in list(branch.tax_benefit_system.variables):
            if variable not in input_variables:
                try:
                    branch.delete_arrays(variable)
                except Exception:
                    pass
        if taxable_social_security is not None:
            branch.populations["tax_unit"].get_holder(
                "tax_unit_taxable_social_security"
            ).set_input(YEAR, taxable_social_security)
        return np.asarray(branch.tax_unit("income_tax", YEAR)).copy()
    finally:
        simulation.branches.pop(name)
        del branch
        gc.collect()


def _release_system_backreference(simulation):
    if getattr(simulation.tax_benefit_system, "simulation", None) is simulation:
        del simulation.tax_benefit_system.simulation


def test_sequential_tob_matches_main_elementwise_and_reuses_states(monkeypatch):
    dataset = build_chunking_dataset()
    baseline = make_simulation(dataset)
    old_law_inclusion = np.asarray(
        baseline.calculate("tax_unit_taxable_social_security_pre_1993", YEAR)
    ).copy()
    # These are main's OASDI and total algorithms, including separate no-SS
    # branches and the signed differences rather than per-tax-unit floors.
    oasdi_no_ss = _main_counterfactual(baseline, "oasdi_no_ss")
    old_law = _main_counterfactual(baseline, "oasdi_old_law", old_law_inclusion)
    current = np.asarray(baseline.calculate("income_tax", YEAR)).copy()
    total_no_ss = _main_counterfactual(baseline, "tob_calc")
    expected = {
        "tob_revenue_oasdi": old_law - oasdi_no_ss,
        "tob_revenue_total": current - total_no_ss,
    }
    expected["tob_revenue_medicare_hi"] = (
        expected["tob_revenue_total"] - expected["tob_revenue_oasdi"]
    )
    weights = np.asarray(baseline.calculate("tax_unit_weight", YEAR)).copy()
    _release_system_backreference(baseline)
    del baseline
    gc.collect()

    simulation = make_simulation(dataset)
    simulation_type = type(simulation)
    original_get_branch = simulation_type.get_branch
    names = []
    references = []

    def get_branch(parent, name="branch", clone_system=False):
        is_tob = parent is simulation and name.startswith("_tob_")
        if is_tob:
            assert all(reference() is None for reference in references)
        branch = original_get_branch(parent, name, clone_system=clone_system)
        if is_tob:
            names.append(name)
            references.append(weakref.ref(branch))
        return branch

    monkeypatch.setattr(simulation_type, "get_branch", get_branch)
    for variable in (
        "tob_revenue_oasdi",
        "tob_revenue_medicare_hi",
        "tob_revenue_total",
    ):
        actual = np.asarray(simulation.calculate(variable, YEAR))
        np.testing.assert_array_equal(actual, expected[variable])
        assert np.sum(actual * weights) == np.sum(expected[variable] * weights)
        assert all(reference() is None for reference in references)

    assert names == ["_tob_no_social_security", "_tob_pre_1993_social_security"]
    assert not any(name.startswith("_tob_") for name in simulation.branches)
    _release_system_backreference(simulation)
    del simulation
    gc.collect()
