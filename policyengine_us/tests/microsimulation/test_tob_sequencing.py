"""Sequential TOB counterfactuals equal the original signed main formulas."""

import gc
import weakref

import numpy as np
import pytest

from policyengine_us.tests.microsimulation.test_calculate_chunked import (
    YEAR,
    _release_reference_simulation,
    build_chunking_dataset,
    frozen_heap,
    lent_parameter_history,
    make_simulation,
)


@pytest.fixture(autouse=True)
def frozen_unchanged_heap():
    # In CI this file shares the microsimulation base group's single pytest
    # process, and it currently sorts last. With the heap frozen, collections
    # scan only what this test creates, including every simulation and branch
    # the weak-reference checks follow.
    with frozen_heap():
        yield


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
        return np.asarray(branch.tax_unit("income_tax_chapter_1", YEAR)).copy()
    finally:
        simulation.branches.pop(name)
        _release_reference_simulation(branch)
        del branch
        gc.collect()


def test_sequential_tob_matches_main_elementwise_and_reuses_states(monkeypatch):
    dataset = build_chunking_dataset()
    # Main's algorithm is the reference. Its branches change no parameter, so
    # they lend the unchanged tree instead of copying it; the helper's branches
    # below, which this test checks, keep ordinary clones.
    with lent_parameter_history():
        baseline = make_simulation(dataset)
        # Main caps old-law inclusion at actual inclusion, read before any branch.
        old_law_inclusion = np.minimum(
            np.asarray(
                baseline.calculate("tax_unit_taxable_social_security_pre_1993", YEAR)
            ),
            np.asarray(baseline.calculate("tax_unit_taxable_social_security", YEAR)),
        ).copy()
        # These are main's OASDI and total algorithms, including separate no-SS
        # branches and the signed differences rather than per-tax-unit floors.
        oasdi_no_ss = _main_counterfactual(baseline, "oasdi_no_ss")
        old_law = _main_counterfactual(baseline, "oasdi_old_law", old_law_inclusion)
        current = np.asarray(baseline.calculate("income_tax_chapter_1", YEAR)).copy()
        total_no_ss = _main_counterfactual(baseline, "tob_calc")
        weights = np.asarray(baseline.calculate("tax_unit_weight", YEAR)).copy()
        _release_reference_simulation(baseline)
        del baseline
        gc.collect()
    expected = {
        "tob_revenue_oasdi": old_law - oasdi_no_ss,
        "tob_revenue_total": current - total_no_ss,
    }
    expected["tob_revenue_medicare_hi"] = (
        expected["tob_revenue_total"] - expected["tob_revenue_oasdi"]
    )

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

    assert names == ["_tob_pre_1993_social_security", "_tob_no_social_security"]
    assert not any(name.startswith("_tob_") for name in simulation.branches)
    _release_reference_simulation(simulation)
    del simulation
    gc.collect()
