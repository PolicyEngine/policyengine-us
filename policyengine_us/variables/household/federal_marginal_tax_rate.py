from policyengine_us.model_api import *
from policyengine_us.variables.household.marginal_tax_rate_helpers import (
    compute_component_mtr,
)


class federal_marginal_tax_rate(Variable):
    label = "federal marginal tax rate"
    documentation = (
        "Marginal change in federal income tax per dollar of additional earnings."
        " Simulated only where marginal_tax_rate_computed is true, that is,"
        " for the top simulation.marginal_tax_rate_adults earners among the"
        " adults in each household; zero for everyone else."
    )
    entity = Person
    definition_period = YEAR
    value_type = float
    unit = "/1"

    def formula(person, period, parameters):
        return compute_component_mtr(
            person, period, parameters, "income_tax", "federal_mtr"
        )
