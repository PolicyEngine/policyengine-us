from policyengine_us.model_api import *


class ma_ccfa_eligible_child(Variable):
    value_type = bool
    entity = Person
    label = "Eligible child for Massachusetts Child Care Financial Assistance (CCFA)"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/financial-assistance-policy-guide"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.age_limits

        age = person("age", period)
        is_disabled = person("is_disabled", period)

        # Age limits: under 13, or under 16 if disabled
        age_limit = where(is_disabled, p.disabled_child, p.regular_child)
        age_eligible = age < age_limit

        # Must be dependent
        is_dependent = person("is_tax_unit_dependent", period)

        # Immigration status check
        immigration_eligible = person("ma_ccfa_immigration_eligible", period)

        return age_eligible & is_dependent & immigration_eligible
