from policyengine_us.model_api import *
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    compute_component_mtr,
)


class fica_marginal_tax_rate(Variable):
    label = "FICA marginal tax rate"
    documentation = (
        "Marginal change in employee payroll tax per dollar of additional earnings."
        " Simulated only where marginal_tax_rate_computed is true: for up to"
        " simulation.marginal_tax_rate_adults adults per household, those with"
        " the highest market income. Zero for everyone else."
    )
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):
        return compute_component_mtr(
            person, period, parameters, "employee_payroll_tax", "fica_mtr"
        )
