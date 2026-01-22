from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)
from policyengine_us.variables.gov.hhs.medicaid.costs.per_capita_cost_helpers import (
    calculate_per_capita_cost,
)


class medicaid_cost_if_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Per capita Medicaid cost by eligibility group & state"
    unit = USD
    definition_period = YEAR
    defined_for = "is_medicaid_eligible"

    def formula(person, period, parameters):
        group = person("medicaid_group", period)
        return calculate_per_capita_cost(
            person,
            period,
            parameters,
            group,
            MedicaidGroup,
            groups=[
                MedicaidGroup.AGED_DISABLED,
                MedicaidGroup.CHILD,
                MedicaidGroup.EXPANSION_ADULT,
                MedicaidGroup.NON_EXPANSION_ADULT,
            ],
        )
