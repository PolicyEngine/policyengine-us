from policyengine_us.model_api import *
from policyengine_us.variables.gov.simulation.behavioral_response_measurements import (
    PRE_RESPONSE_INPUTS,
)


def create_perturbed_branch(simulation, period, branch_name, increments):
    """Branch in which each variable in ``increments`` rises by its increment.

    The branch keeps the simulation's inputs and recomputes everything else,
    so it matches a fresh simulation of the same households with the raised
    inputs. Simulations store an aggregate such as ``employment_income`` on
    its pre-response input (``employment_income_before_lsr``), and some
    programs read that input directly; TANF's earned income does. Raising the
    aggregate itself would hide the increase from those programs, so the
    increase goes to the variable that holds the input.

    Args:
        simulation: The simulation to branch from.
        period: The period whose inputs rise.
        branch_name: Name of the branch; the caller deletes it when done.
        increments: Person-level increase for each raised variable.

    Returns:
        The branch simulation.
    """
    input_variables = set(simulation.input_variables)
    branch = simulation.get_branch(branch_name)
    for variable in simulation.tax_benefit_system.variables:
        if variable not in input_variables:
            branch.delete_arrays(variable)
    for variable, increment in increments.items():
        if variable not in input_variables:
            variable = PRE_RESPONSE_INPUTS.get(variable, variable)
        value = simulation.calculate(variable, period) + increment
        # The branch still holds the base values cached for the months of
        # the period, which monthly programs such as TANF read.
        branch.delete_arrays(variable, period)
        branch.set_input(variable, period, value)
    return branch


def earnings_increments(person, period, increase):
    """Split an earnings increase across wages and self-employment income.

    Follows each person's current mix of wages, non-SSTB and SSTB
    self-employment income, putting the increase on wages when the person
    has no positive earnings.
    """
    self_employment_income = max_(0, person("self_employment_income", period))
    sstb_self_employment_income = max_(0, person("sstb_self_employment_income", period))
    total_self_employment_income = self_employment_income + sstb_self_employment_income
    non_sstb_share = np.divide(
        self_employment_income,
        total_self_employment_income,
        out=np.ones_like(total_self_employment_income, dtype=np.float64),
        where=total_self_employment_income > 0,
    )
    wage_share = person("emp_self_emp_ratio", period)
    self_employment_increase = increase * (1 - wage_share)
    return {
        "employment_income": increase * wage_share,
        "self_employment_income": self_employment_increase * non_sstb_share,
        "sstb_self_employment_income": self_employment_increase * (1 - non_sstb_share),
    }


def marginal_earnings_change(person, period, parameters, measure, branch_prefix):
    """Change in ``measure`` per dollar of additional earnings, for each adult.

    For each of the first ``simulation.marginal_tax_rate_adults`` adults in
    every household, ranked by market income, a branch raises that adult's
    earnings by ``simulation.marginal_tax_rate_delta`` and records how much
    ``measure`` changes per dollar.

    Args:
        person: The person entity.
        period: The simulation period.
        parameters: The parameter tree.
        measure: Function of a person population returning a person-level
            array, e.g. the person's household net income.
        branch_prefix: Unique prefix for branch names to avoid conflicts.

    Returns:
        A tuple of the change per dollar for each measured adult (zero for
        everyone else) and a mask of the measured adults.
    """
    delta = parameters(period).simulation.marginal_tax_rate_delta
    adult_count = parameters(period).simulation.marginal_tax_rate_adults
    simulation = person.simulation
    base = measure(person)
    adult_indexes = person("adult_earnings_index", period)
    change = np.zeros(person.count, dtype=np.float32)
    measured = np.zeros(person.count, dtype=bool)
    for adult_index in range(1, 1 + adult_count):
        branch_name = f"{branch_prefix}_for_adult_{adult_index}"
        mask = adult_index == adult_indexes
        branch = create_perturbed_branch(
            simulation,
            period,
            branch_name,
            earnings_increments(person, period, mask * delta),
        )
        alt = measure(branch.person)
        change += where(mask, (alt - base) / delta, 0)
        measured |= mask
        del simulation.branches[branch_name]
    return change, measured


def compute_component_mtr(person, period, parameters, tax_variable, branch_prefix):
    """Compute the marginal tax rate for a specific tax component.

    Uses the same counterfactual branch as marginal_tax_rate: raises earnings
    by delta and measures the change in the given tax_unit-level tax
    variable, aggregated to the household level for consistency with how
    marginal_tax_rate uses household_net_income.

    Args:
        person: The person entity.
        period: The simulation period.
        parameters: The parameter tree.
        tax_variable: Name of the tax_unit variable to measure
            (e.g. "income_tax", "state_income_tax", "employee_payroll_tax").
        branch_prefix: Unique prefix for branch names to avoid conflicts.

    Returns:
        Array of marginal tax rates per person.
    """

    def household_tax(population):
        is_head = population("is_tax_unit_head", period)
        return population.household.sum(
            population.tax_unit(tax_variable, period) * is_head
        )

    change, _ = marginal_earnings_change(
        person, period, parameters, household_tax, branch_prefix
    )
    return change
