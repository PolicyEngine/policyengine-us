from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)


class dc_medicaid_group(Variable):
    value_type = Enum
    possible_values = MedicaidGroup
    default_value = MedicaidGroup.EXPANSION_ADULT
    entity = Person
    label = "DC Medicaid eligibility group"
    definition_period = YEAR
    defined_for = "dc_medicaid_enrolled"

    def formula(person, period, parameters):
        # Determine group based on demographics
        age = person("age", period)
        is_pregnant = person("is_pregnant", period)
        is_disabled = person("is_ssi_recipient_for_medicaid", period)

        # Use DC's child_max_age parameter for consistency with income eligibility
        p_elig = parameters(period).gov.states.dc.dhcf.medicaid.eligibility
        is_child = age <= p_elig.child_max_age

        # Get aged threshold from the federal Medicaid adult age range parameter
        p_adult = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.adult.age_range
        aged_threshold = p_adult.thresholds[-1]
        is_aged_disabled = is_disabled | (age >= aged_threshold)
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
