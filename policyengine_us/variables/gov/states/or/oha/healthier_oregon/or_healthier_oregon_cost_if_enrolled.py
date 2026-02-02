from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)
from policyengine_us.variables.gov.hhs.medicaid.costs.per_capita_cost_helpers import (
    calculate_per_capita_cost,
)


class or_healthier_oregon_cost_if_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Per capita Oregon Healthier Oregon cost by eligibility group"
    unit = USD
    definition_period = YEAR
    defined_for = "or_healthier_oregon_eligible"
    reference = (
        "https://www.oregon.gov/oha/hsd/ohp/pages/healthier-oregon.aspx"
    )

    def formula(person, period, parameters):
        oregon_group = person("or_healthier_oregon_group", period)
        return calculate_per_capita_cost(
            person,
            period,
            parameters,
            oregon_group,
            MedicaidGroup,
            groups=[
                MedicaidGroup.AGED_DISABLED,
                MedicaidGroup.CHILD,
                MedicaidGroup.EXPANSION_ADULT,
                MedicaidGroup.NON_EXPANSION_ADULT,
            ],
        )
