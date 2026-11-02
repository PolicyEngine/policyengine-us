"""Over a dataset, the SPM subtracts what parents reported paying for child care.

Datasets fill spm_unit_pre_subsidy_childcare_expenses from the ASEC's
SPM_CHILDCAREXPNS, which holds what parents paid after any subsidy. So baseline
policy keeps that amount, and a reform moves it by the change in subsidy. These
tests run the rule over the shipped population rather than the situations in
test_spm_child_care_subsidy_invariants.py, so the dataset flag and the reform's
baseline arm come from loading a real file.
"""

import numpy as np

from policyengine_us.tests.microsimulation.populace_fixture import (
    default_population_sample,
)

PERIOD = 2026
TOLERANCE = 0.01
FLAT_SUBSIDY = 1_000


def spm_arrays(simulation):
    return {
        name: np.asarray(simulation.calculate(name, PERIOD), dtype=float)
        for name in (
            "child_care_subsidies",
            "spm_unit_capped_work_childcare_expenses",
            "spm_unit_head_spouse_earned_cap",
            "spm_unit_pre_subsidy_childcare_expenses",
            "spm_unit_work_expenses",
        )
    }


def test_baseline_expense_is_the_reported_amount_over_the_whole_population():
    from policyengine_us import Microsimulation

    simulation = Microsimulation()  # populace_us_2024, full file
    reported = simulation.calculate(
        "spm_unit_pre_subsidy_childcare_expenses", PERIOD
    ).values
    work = simulation.calculate("spm_unit_work_expenses", PERIOD).values
    cap = simulation.calculate("spm_unit_head_spouse_earned_cap", PERIOD).values
    expense = simulation.calculate(
        "spm_unit_capped_work_childcare_expenses", PERIOD
    ).values

    # The identity would hold trivially if nobody reported paying.
    assert (reported > 0).sum() > 1_000
    assert (expense == np.minimum(work + reported, cap)).all()


def test_reform_moves_the_reported_expense_by_the_change_in_subsidy():
    from policyengine_core.reforms import Reform

    from policyengine_us import Microsimulation
    from policyengine_us.model_api import SPMUnit, USD, YEAR, Variable

    class child_care_subsidies(Variable):
        value_type = float
        entity = SPMUnit
        definition_period = YEAR
        label = "Child care subsidies"
        unit = USD

        def formula(spm_unit, period, parameters):
            return np.full(spm_unit.count, FLAT_SUBSIDY, dtype=float)

    class FlatSubsidy(Reform):
        def apply(self):
            self.update_variable(child_care_subsidies)

    dataset = default_population_sample()
    baseline = spm_arrays(Microsimulation(dataset=dataset))
    simulation = Microsimulation(dataset=dataset, reform=FlatSubsidy)
    reformed = spm_arrays(simulation)
    arm = spm_arrays(simulation.baseline)

    # The reform's baseline arm matches a simulation with no reform.
    for name, values in baseline.items():
        np.testing.assert_array_equal(arm[name], values, err_msg=name)

    reported = baseline["spm_unit_pre_subsidy_childcare_expenses"]
    assert (reformed["child_care_subsidies"] == FLAT_SUBSIDY).all()
    # The slice has to hold units the old rule got wrong: the model pays them a
    # subsidy and they reported paying, so it netted one from the other.
    paid = (baseline["child_care_subsidies"] > 0) & (reported > 0)
    assert paid.any()
    np.testing.assert_allclose(
        baseline["spm_unit_capped_work_childcare_expenses"][paid],
        np.minimum(
            baseline["spm_unit_work_expenses"] + reported,
            baseline["spm_unit_head_spouse_earned_cap"],
        )[paid],
        atol=TOLERANCE,
    )
    # And units on each side of the floor.
    assert ((reported > 0) & (reported < FLAT_SUBSIDY)).any()
    assert (reported > FLAT_SUBSIDY).any()

    change = FLAT_SUBSIDY - baseline["child_care_subsidies"]
    expected = np.minimum(
        reformed["spm_unit_work_expenses"] + np.maximum(reported - change, 0),
        reformed["spm_unit_head_spouse_earned_cap"],
    )
    np.testing.assert_allclose(
        reformed["spm_unit_capped_work_childcare_expenses"],
        expected,
        atol=TOLERANCE,
    )
    # Some unit's expense has to move, or the comparison above proves nothing.
    assert (
        reformed["spm_unit_capped_work_childcare_expenses"]
        < baseline["spm_unit_capped_work_childcare_expenses"]
    ).any()
