from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)


class dc_medicaid_cost_if_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Per capita DC Medicaid/Alliance cost by eligibility group"
    unit = USD
    definition_period = YEAR
    defined_for = "dc_medicaid_enrolled"
    reference = "https://dhcf.dc.gov/alliance"

    def formula(person, period, parameters):
        # Reuse the exact same cost calculation as federal Medicaid
        # DC Medicaid provides equivalent benefits
        state = person.household("state_code", period)

        # Since DC Medicaid enrollees may not have medicaid_category set,
        # we need to determine their group based on demographics
        age = person("age", period)
        is_pregnant = person("is_pregnant", period)
        is_disabled = person("is_ssi_recipient_for_medicaid", period)

        # Map to appropriate group
        is_child = age < 19
        is_aged_disabled = is_disabled | (age >= 65)
        is_non_expansion_adult = is_pregnant & ~is_child & ~is_aged_disabled
        is_expansion_adult = (
            ~is_child & ~is_aged_disabled & ~is_non_expansion_adult
        )

        # Determine the group
        group = select(
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

        # Get the per capita costs from parameters
        p = parameters(period).calibration.gov.hhs.medicaid

        # Get spending and enrollment by group
        aged_spend = p.spending.by_eligibility_group.aged[state]
        disabled_spend = p.spending.by_eligibility_group.disabled[state]
        child_spend = p.spending.by_eligibility_group.child[state]
        expansion_adult_spend = (
            p.spending.by_eligibility_group.expansion_adults[state]
        )
        non_expansion_adult_spend = (
            p.spending.by_eligibility_group.non_expansion_adults[state]
        )

        aged_enroll = p.enrollment.aged[state]
        disabled_enroll = p.enrollment.disabled[state]
        child_enroll = p.enrollment.child[state]
        expansion_adult_enroll = p.enrollment.expansion_adults[state]
        non_expansion_adult_enroll = p.enrollment.non_expansion_adults[state]

        # Combine aged and disabled
        aged_disabled_spend = aged_spend + disabled_spend
        aged_disabled_enroll = aged_enroll + disabled_enroll

        # Select values based on group
        spend = select(
            [
                group == MedicaidGroup.AGED_DISABLED,
                group == MedicaidGroup.CHILD,
                group == MedicaidGroup.EXPANSION_ADULT,
                group == MedicaidGroup.NON_EXPANSION_ADULT,
            ],
            [
                aged_disabled_spend,
                child_spend,
                expansion_adult_spend,
                non_expansion_adult_spend,
            ],
            default=0,
        )

        enroll = select(
            [
                group == MedicaidGroup.AGED_DISABLED,
                group == MedicaidGroup.CHILD,
                group == MedicaidGroup.EXPANSION_ADULT,
                group == MedicaidGroup.NON_EXPANSION_ADULT,
            ],
            [
                aged_disabled_enroll,
                child_enroll,
                expansion_adult_enroll,
                non_expansion_adult_enroll,
            ],
            default=0,
        )

        # Calculate per capita cost
        per_capita = p.totals.per_capita[group]
        mask = enroll > 0
        per_capita[mask] = spend[mask] / enroll[mask]

        return per_capita
