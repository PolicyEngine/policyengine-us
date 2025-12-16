from policyengine_us.model_api import *


class or_healthier_oregon_cost(Variable):
    value_type = float
    entity = Person
    label = "Oregon Healthier Oregon benefit cost"
    unit = USD
    definition_period = YEAR
    defined_for = "or_healthier_oregon_eligible"
    reference = [
        "https://www.oregon.gov/oha/hsd/ohp/pages/healthier-oregon.aspx",
    ]
    documentation = """
    Oregon Healthier Oregon provides full OHP (Oregon Health Plan) benefits,
    equivalent to Medicaid coverage. The cost is calculated using the same
    per capita Medicaid costs by eligibility group.
    """

    adds = ["or_healthier_oregon_cost_if_enrolled"]


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

        # Determine group based on demographics
        age = person("age", period)
        is_pregnant = person("is_pregnant", period)
        is_disabled = person("is_ssi_recipient_for_medicaid", period)

        is_child = age < 19
        is_aged_disabled = is_disabled | (age >= 65)
        is_non_expansion_adult = is_pregnant & ~is_child & ~is_aged_disabled
        is_expansion_adult = (
            ~is_child & ~is_aged_disabled & ~is_non_expansion_adult
        )

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
