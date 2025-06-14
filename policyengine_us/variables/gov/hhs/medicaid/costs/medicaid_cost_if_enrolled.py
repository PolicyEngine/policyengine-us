from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
    MedicaidGroup,
)


class medicaid_cost_if_enrolled(Variable):
    value_type = float
    entity = Person
    label = "Per capita Medicaid cost by eligibility group & state"
    unit = USD
    definition_period = YEAR
    defined_for = "is_medicaid_eligible"

    def formula(person, period, parameters):
        state = person.household("state_code", period)
        group = person("medicaid_group", period)

        p = parameters(period).calibration.gov.hhs.medicaid

        # Handle each group type separately
        is_aged_disabled = group == MedicaidGroup.AGED_DISABLED
        is_child = group == MedicaidGroup.CHILD
        is_expansion_adult = group == MedicaidGroup.EXPANSION_ADULT
        is_non_expansion_adult = group == MedicaidGroup.NON_EXPANSION_ADULT

        # Calculate spend and enrollment for each group
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

        # Combine aged and disabled for AGED_DISABLED group
        aged_disabled_spend = aged_spend + disabled_spend
        aged_disabled_enroll = aged_enroll + disabled_enroll

        # Select the right values based on group
        spend = select(
            [
                is_aged_disabled,
                is_child,
                is_expansion_adult,
                is_non_expansion_adult,
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
                is_aged_disabled,
                is_child,
                is_expansion_adult,
                is_non_expansion_adult,
            ],
            [
                aged_disabled_enroll,
                child_enroll,
                expansion_adult_enroll,
                non_expansion_adult_enroll,
            ],
            default=0,
        )

        # Avoid divide‑by‑zero in non‑expansion states by assigning national average.
        per_capita = p.totals.per_capita[group]
        mask = enroll > 0
        per_capita[mask] = spend[mask] / enroll[mask]

        return per_capita
