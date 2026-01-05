from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)


class wa_apple_health_group(Variable):
    """Maps Washington Apple Health eligibility to Medicaid spending groups.

    Apple Health for Kids → CHILD
    Apple Health Expansion → EXPANSION_ADULT
    """

    value_type = Enum
    possible_values = MedicaidGroup
    default_value = MedicaidGroup.NONE
    entity = Person
    label = "Washington Apple Health spending group"
    definition_period = YEAR
    defined_for = StateCode.WA
    reference = [
        "https://www.hca.wa.gov/free-or-low-cost-health-care/i-need-medical-dental-or-vision-care/children",
        "https://www.hca.wa.gov/about-hca/programs-and-initiatives/apple-health-medicaid/apple-health-expansion",
    ]

    def formula(person, period, parameters):
        kids_eligible = person("wa_apple_health_kids_eligible", period)
        expansion_eligible = person(
            "wa_apple_health_expansion_eligible", period
        )

        return select(
            [
                kids_eligible,
                expansion_eligible,
            ],
            [
                MedicaidGroup.CHILD,
                MedicaidGroup.EXPANSION_ADULT,
            ],
            default=MedicaidGroup.NONE,
        )
