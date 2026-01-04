from policyengine_us.model_api import *


class il_pfae_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Illinois Preschool For All Expansion (PFAE)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/pages/preschool-for-all.aspx",
        "https://www.isbe.net/Documents/pdg-eg-grant-enrollment-form.pdf#page=2",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # PFAE eligibility requires:
        # - Basic eligibility (age 3-5, income <= 400% FPL)
        # - AND either:
        #   - Any highest priority factor (direct enrollment), OR
        #   - 2+ secondary priority factors
        basic_eligible = person("il_pfae_basic_eligible", period)
        has_highest_priority = person(
            "il_pfae_has_highest_priority_factor", period
        )
        secondary_count = person(
            "il_pfae_secondary_priority_factor_count", period
        )
        return basic_eligible & (has_highest_priority | (secondary_count >= 2))
