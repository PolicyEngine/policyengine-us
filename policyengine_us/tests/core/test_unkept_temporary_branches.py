"""Formulas that remove a temporary branch calculate when it was never kept.

``marginal_tax_rate`` and its component rates (through
``marginal_earnings_change``), ``marginal_tax_rate_on_capital_gains``,
``employer_ss_tax_income_tax_revenue`` and
``employer_medicare_tax_income_tax_revenue`` each create a branch of the
simulation with ``get_branch``, calculate in it, then remove it from
``simulation.branches``. policyengine-core's read-only simulations
(``Simulation.make_read_only``, not yet released) give a new branch for a name
they have not registered and do not keep it in ``branches``, so
``del simulation.branches[name]`` raised ``KeyError`` on them.

The released core keeps every branch ``get_branch`` creates, so these tests
give chosen simulations a ``get_branch`` that removes each new branch from
``branches`` before returning it, as a read-only simulation keeps none. Each
formula must give the value it gives on a plain simulation of the same
household, after creating its branch on the simulation that keeps none.

Cost: each case builds two one-person simulations; the reform case also
applies a parametric reform to each, the largest part of the file's cost.
"""

import numpy as np
import pytest
from policyengine_core.reforms import Reform
from policyengine_core.simulations import Simulation as CoreSimulation

from policyengine_us import Simulation

YEAR = 2024


def one_person_household(**person_inputs):
    """A California household of one 40-year-old with ``person_inputs`` in YEAR."""
    person = {"age": {YEAR: 40}}
    person.update({name: {YEAR: value} for name, value in person_inputs.items()})
    return {
        "people": {"person": person},
        "tax_units": {"tax_unit": {"members": ["person"]}},
        "spm_units": {"spm_unit": {"members": ["person"]}},
        "families": {"family": {"members": ["person"]}},
        "marital_units": {"marital_unit": {"members": ["person"]}},
        "households": {
            "household": {"members": ["person"], "state_code": {YEAR: "CA"}}
        },
    }


# Including employer payroll taxes in income makes the employer revenue
# formulas branch; with it off they return zero without branching.
EMPLOYER_PAYROLL_TAX_IN_INCOME = {
    "gov.contrib.crfb.tax_employer_payroll_tax.in_effect": {
        "2020-01-01.2100-12-31": True
    },
    "gov.contrib.crfb.tax_employer_payroll_tax.percentage": {
        "2020-01-01.2100-12-31": 1.0
    },
}


@pytest.fixture
def stop_keeping_new_branches(monkeypatch):
    """Return a function that stops a simulation keeping branches it creates.

    After ``stop_keeping_new_branches(simulation)``, ``simulation.get_branch``
    with a name it has not registered still creates and returns a branch, but
    removes it from ``simulation.branches`` first, as a read-only simulation
    keeps no branch it creates. The branch itself keeps the branches it
    creates, as a read-only simulation's branches do. The function returns the
    list of names of branches the simulation created and did not keep, which
    grows as it calculates.
    """
    unkept_branch_names = []
    simulations_keeping_no_new_branches = []
    core_get_branch = CoreSimulation.get_branch

    def get_branch_keeping_none(self, name="branch", clone_system=False):
        creating = name != self.branch_name and name not in self.branches
        branch = core_get_branch(self, name, clone_system)
        keeps_none = any(
            self is simulation for simulation in simulations_keeping_no_new_branches
        )
        if creating and keeps_none:
            del self.branches[name]
            unkept_branch_names.append(name)
        return branch

    monkeypatch.setattr(CoreSimulation, "get_branch", get_branch_keeping_none)

    def stop_keeping(simulation):
        simulations_keeping_no_new_branches.append(simulation)
        return unkept_branch_names

    return stop_keeping


def test_the_test_simulation_keeps_no_branch_it_creates(stop_keeping_new_branches):
    simulation = Simulation(situation=one_person_household(employment_income=50_000))
    registered_before = dict(simulation.branches)
    unkept_branch_names = stop_keeping_new_branches(simulation)
    first = simulation.get_branch("temporary")
    second = simulation.get_branch("temporary")
    assert first is not second
    assert first.parent_branch is simulation
    assert simulation.branches == registered_before
    assert unkept_branch_names == ["temporary", "temporary"]
    nested = first.get_branch("nested")
    assert first.branches == {"nested": nested}


# Each case: the household, the parameter changes it is simulated under, and
# for each formula the name it gives the branch it creates.
CASES = [
    pytest.param(
        one_person_household(employment_income=50_000, long_term_capital_gains=20_000),
        None,
        {
            "marginal_tax_rate": "mtr_for_adult_1",
            "marginal_tax_rate_on_capital_gains": "adult_1_cg_rise",
        },
        id="current law",
    ),
    pytest.param(
        one_person_household(employment_income=50_000),
        EMPLOYER_PAYROLL_TAX_IN_INCOME,
        {
            "employer_ss_tax_income_tax_revenue": "without_employer_ss",
            "employer_medicare_tax_income_tax_revenue": "without_employer_medicare",
        },
        id="employer payroll tax in income",
    ),
]


def build_simulation(situation, parameter_changes):
    if parameter_changes is None:
        return Simulation(situation=situation)
    reform = Reform.from_dict(parameter_changes, country_id="us")
    return Simulation(situation=situation, reform=reform)


@pytest.mark.parametrize("situation, parameter_changes, branch_name_of_variable", CASES)
def test_formulas_give_their_plain_values_when_their_branches_are_not_kept(
    stop_keeping_new_branches, situation, parameter_changes, branch_name_of_variable
):
    plain = build_simulation(situation, parameter_changes)
    plain_values = {
        variable: plain.calculate(variable, YEAR)
        for variable in branch_name_of_variable
    }

    simulation = build_simulation(situation, parameter_changes)
    registered_before = dict(simulation.branches)
    unkept_branch_names = stop_keeping_new_branches(simulation)
    for variable, branch_name in branch_name_of_variable.items():
        value = simulation.calculate(variable, YEAR)
        # A zero would also come from a formula that returned before branching.
        assert np.all(plain_values[variable] != 0), variable
        np.testing.assert_array_equal(value, plain_values[variable], err_msg=variable)
        assert branch_name in unkept_branch_names, variable
    assert simulation.branches == registered_before


@pytest.mark.parametrize("situation, parameter_changes, branch_name_of_variable", CASES)
def test_formulas_refuse_to_calculate_in_a_branch_with_their_branch_name(
    situation, parameter_changes, branch_name_of_variable
):
    """In a branch with the name a formula gives its branch, it changes nothing.

    There ``get_branch`` returns the simulation being calculated, so raising
    its inputs or neutralizing variables in its system would change that
    simulation, and its result would be wrong.
    """
    simulation = build_simulation(situation, parameter_changes)
    for variable, branch_name in branch_name_of_variable.items():
        branch = simulation.get_branch(branch_name)
        system = branch.tax_benefit_system
        neutralized_before = {
            name
            for name, definition in system.variables.items()
            if definition.is_neutralized
        }
        inputs_before = {
            name: branch.calculate(name, YEAR).copy()
            for name in ("employment_income_before_lsr", "long_term_capital_gains")
        }
        with pytest.raises(ValueError, match=branch_name):
            branch.calculate(variable, YEAR)
        neutralized_after = {
            name
            for name, definition in system.variables.items()
            if definition.is_neutralized
        }
        assert neutralized_after == neutralized_before, variable
        for name, value in inputs_before.items():
            np.testing.assert_array_equal(
                branch.calculate(name, YEAR), value, err_msg=f"{variable}: {name}"
            )
