from policyengine_us.model_api import *


class medicare_part_b_premium(Variable):
    value_type = float
    entity = Person
    label = "Medicare Part B premium"
    unit = USD
    definition_period = YEAR
    defined_for = "medicare_part_b_enrolled"
    reference = "https://www.medicare.gov/basics/costs/medicare-costs#partB"
    documentation = (
        "Annual Medicare Part B premium paid out of pocket by a Part B "
        "enrollee, net of the standard premium a state pays through a "
        "Medicare Savings Program or a Medicaid buy-in for SSI recipients. "
        "Never below zero or above the gross premium."
    )

    def formula(person, period, parameters):
        gross_premium = person("gross_medicare_part_b_premium", period)
        # Both pathways pay the same standard premium, so a person covered
        # by both is covered once.
        state_paid = max_(
            person("msp_part_b_premium_coverage", period),
            person("medicaid_part_b_buy_in_premium_coverage", period),
        )
        return max_(gross_premium - state_paid, 0)
