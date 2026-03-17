from policyengine_us.model_api import *
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    compute_component_mtr,
)


class federal_marginal_tax_rate(Variable):
    label = "federal marginal tax rate"
    documentation = (
        "Marginal change in federal income tax per dollar of additional earnings."
    )
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):
        return compute_component_mtr(
            person, period, parameters, "income_tax", "federal_mtr"
        )
