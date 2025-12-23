from policyengine_us.model_api import *


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
        from policyengine_us.variables.gov.hhs.medicaid.costs.medicaid_group import (
            MedicaidGroup,
        )

        state = person.household("state_code", period)
        group = person("or_healthier_oregon_group", period)

        # Get per capita costs from Medicaid parameters
        p = parameters(period).calibration.gov.hhs.medicaid

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

        aged_disabled_spend = aged_spend + disabled_spend
        aged_disabled_enroll = aged_enroll + disabled_enroll

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

        per_capita = p.totals.per_capita[group]
        mask = enroll > 0
        per_capita[mask] = spend[mask] / enroll[mask]

        return per_capita
