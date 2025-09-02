from policyengine_us.model_api import *


class ma_ccfa_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Massachusetts Child Care Financial Assistance (CCFA)"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/eecs-financial-assistance-policy-guide-february-1-2022/download#page=10"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.age_threshold
        age = person("monthly_age", period)
        is_disabled = person("is_disabled", period)
        age_limit = where(is_disabled, p.disabled_child, p.child)
        age_eligible = age < age_limit
        is_dependent = person("is_tax_unit_dependent", period)
        immigration_eligible = person(
            "ma_ccfa_immigration_status_eligible", period
        )

        return age_eligible & is_dependent & immigration_eligible
