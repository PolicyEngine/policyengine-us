from policyengine_us.model_api import *
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    compute_component_mtr,
)


class state_marginal_tax_rate(Variable):
    label = "state marginal tax rate"
    documentation = (
        "Marginal change in state income tax per dollar of additional earnings."
    )
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):
        return compute_component_mtr(
            person, period, parameters, "state_income_tax", "state_mtr"
        )
