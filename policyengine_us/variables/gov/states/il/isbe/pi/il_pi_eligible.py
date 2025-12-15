from policyengine_us.model_api import *


class il_pi_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Illinois Prevention Initiative"
    definition_period = YEAR
    reference = "https://www.isbe.net/Pages/Birth-to-Age-3-Years.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Eligibility requires: (child under 3 OR pregnant),
        # income <= 400% FPL, and at least 1 risk factor.
        eligible_child = person("il_pi_eligible_child", period)
        eligible_pregnant = person("il_pi_eligible_pregnant", period)
        age_eligible = eligible_child | eligible_pregnant
        income_eligible = person("il_pi_income_eligible", period)
        risk_eligible = person("il_pi_risk_eligible", period)
        return age_eligible & income_eligible & risk_eligible
