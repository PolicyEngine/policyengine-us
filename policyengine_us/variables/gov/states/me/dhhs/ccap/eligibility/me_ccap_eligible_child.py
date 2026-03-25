from policyengine_us.model_api import *


class me_ccap_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Maine CCAP"
    definition_period = MONTH
    defined_for = StateCode.ME
    reference = "https://www.maine.gov/dhhs/sites/maine.gov.dhhs/files/inline-files/CCAP%20Full%20Rule%208.18.2025_1.pdf#page=11"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.me.dhhs.ccap.age_limit
        age = person("monthly_age", period)
        is_disabled = person("is_disabled", period.this_year)
        age_limit = where(is_disabled, p.special_needs, p.child)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        immigration_eligible = person(
            "is_ccdf_immigration_eligible_child", period.this_year
        )
        return age_eligible & is_dependent & immigration_eligible
