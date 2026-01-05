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
    reference = "https://dhcf.dc.gov/node/1809101"

    def formula(person, period, parameters):
        state = person.household("state_code", period)
        group = person("dc_medicaid_group", period)

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

        # Calculate per capita cost from spend/enroll, falling back to
        # national average when enrollment is zero
        default_per_capita = p.totals.per_capita[group]
        mask = enroll > 0
        per_capita = where(
            mask,
            spend / max_(enroll, 1),  # Avoid divide-by-zero
            default_per_capita,
        )

        return per_capita
