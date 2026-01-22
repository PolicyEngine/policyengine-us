from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)


class or_healthier_oregon_group(Variable):
    value_type = Enum
    possible_values = MedicaidGroup
    default_value = MedicaidGroup.NONE
    entity = Person
    label = "Oregon Healthier Oregon Medicaid spending group"
    definition_period = YEAR
    defined_for = StateCode.OR
    reference = (
        "https://www.oregon.gov/oha/hsd/ohp/pages/healthier-oregon.aspx"
    )

    def formula(person, period, parameters):
        age = person("age", period)
        is_pregnant = person("is_pregnant", period)
        is_disabled = person("is_ssi_recipient_for_medicaid", period)

        # Use the Oregon Healthier Oregon child_max_age parameter
        p = (
            parameters(period)
            .gov.states["or"]
            .oha.healthier_oregon.eligibility
        )
        is_child = age < p.child_max_age

        is_aged_disabled = is_disabled | (age >= p.aged_threshold)

        is_non_expansion_adult = is_pregnant & ~is_child & ~is_aged_disabled

        is_expansion_adult = (
            ~is_child & ~is_aged_disabled & ~is_non_expansion_adult
        )

        return select(
            [
                is_aged_disabled,
                is_child,
                is_non_expansion_adult,
                is_expansion_adult,
            ],
            [
                MedicaidGroup.AGED_DISABLED,
                MedicaidGroup.CHILD,
                MedicaidGroup.NON_EXPANSION_ADULT,
                MedicaidGroup.EXPANSION_ADULT,
            ],
            default=MedicaidGroup.EXPANSION_ADULT,
        )
