from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)
from policyengine_us.variables.gov.hhs.medicaid.costs.per_capita_cost_helpers import (
    calculate_per_capita_cost,
)


class modeled_medicaid_cost_if_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Modeled Medicaid cost if enrolled"
    unit = USD
    definition_period = YEAR
    defined_for = "is_medicaid_eligible"

    def formula(person, period, parameters):
        return calculate_per_capita_cost(
            person,
            period,
            parameters,
            person("medicaid_group", period),
            MedicaidGroup,
            groups=[
                MedicaidGroup.AGED_DISABLED,
                MedicaidGroup.CHILD,
                MedicaidGroup.EXPANSION_ADULT,
                MedicaidGroup.NON_EXPANSION_ADULT,
            ],
        )
