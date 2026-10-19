from policyengine_us.model_api import *
from policyengine_us.variables.household.expense.retirement._ira_supplied_contributions import (
    IRA_CONTRIBUTION_VARIABLES,
)


def user_set_variables(sim):
    """Names of the variables a counterfactual branch must keep.

    ``sim.input_variables`` lists inputs given when the simulation was built.
    The IRA contribution variables are also kept when the caller set them
    later through ``set_input`` (core records those in ``_user_input_keys``):
    ``ira_contribution_limit`` reads them as supplied, so a branch that
    deleted them would regenerate a different IRA allocation alongside the
    earnings bump. Other later ``set_input`` calls are not kept, because
    model formulas also call ``set_input`` internally (the SSA revenue
    formulas set ``tax_unit_taxable_social_security``), and a branch must
    recompute those.
    """
    names = set(sim.input_variables)
    keys = getattr(sim, "_user_input_keys", None) or ()
    if hasattr(sim, "_get_visible_branch_names"):
        branches = set(sim._get_visible_branch_names())
    else:
        branches = {getattr(sim, "branch_name", "default"), "default"}
    names.update(
        name
        for name, branch, _period in keys
        if name in IRA_CONTRIBUTION_VARIABLES and branch in branches
    )
    return names


def compute_component_mtr(person, period, parameters, tax_variable, branch_prefix):
    """Compute the marginal tax rate for a specific tax component.

    Uses the same counterfactual branch pattern as marginal_tax_rate:
    perturbs earnings by delta and measures the change in the given
    tax_unit-level tax variable, aggregated to the household level
    for consistency with how marginal_tax_rate uses household_net_income.

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
    is_head = person("is_tax_unit_head", period)
    base_tax = person.household.sum(person.tax_unit(tax_variable, period) * is_head)
    delta = parameters(period).simulation.marginal_tax_rate_delta
    adult_count = parameters(period).simulation.marginal_tax_rate_adults
    sim = person.simulation
    mtr_values = np.zeros(person.count, dtype=np.float32)
    adult_indexes = person("adult_earnings_index", period)
    employment_income = person("employment_income", period)
    self_employment_income = person("self_employment_income", period)
    emp_self_emp_ratio = person("emp_self_emp_ratio", period)

    inputs = user_set_variables(sim)
    for adult_index in range(1, 1 + adult_count):
        branch_name = f"{branch_prefix}_for_adult_{adult_index}"
        alt_sim = sim.get_branch(branch_name)
        for variable in sim.tax_benefit_system.variables:
            if variable not in inputs or variable == "employment_income":
                alt_sim.delete_arrays(variable)
        mask = adult_index == adult_indexes
        alt_sim.set_input(
            "employment_income",
            period,
            employment_income + mask * delta * emp_self_emp_ratio,
        )
        alt_sim.set_input(
            "self_employment_income",
            period,
            self_employment_income + mask * delta * (1 - emp_self_emp_ratio),
        )
        alt_person = alt_sim.person
        alt_is_head = alt_person("is_tax_unit_head", period)
        alt_tax = alt_person.household.sum(
            alt_person.tax_unit(tax_variable, period) * alt_is_head
        )
        increase = alt_tax - base_tax
        mtr_values += where(mask, increase / delta, 0)
        del sim.branches[branch_name]
    return mtr_values
