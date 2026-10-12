from policyengine_us.model_api import *


class ms_ccpp_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Mississippi CCPP"
    definition_period = MONTH
    defined_for = StateCode.MS
    reference = "https://www.mdhs.ms.gov/wp-content/uploads/2026/01/CCPP-Policy-Manual_Final_1142025.pdf#page=25"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ms.dhs.ccpp.eligibility
        age = person("age", period.this_year)
        is_special_needs = person("is_disabled", period.this_year)
        # Children must be under 13, or under 19 if they have special needs.
        age_eligible = where(
            is_special_needs,
            age < p.special_needs_child_age_limit,
            age < p.child_age_limit,
        )
        # Children must be citizens or qualified non-citizens (no parent bar).
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & immigration_eligible
