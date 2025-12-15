from policyengine_us.model_api import *


class il_pfae_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Priority for Illinois Preschool For All Expansion (PFAE)"
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # PFAE full-day slots prioritize higher-risk families.
        # Requires: PFA eligibility + higher risk (2+ factors or highest-priority)
        # + lower income (<=200% FPL).
        pfa_eligible = person("il_pfa_eligible", period)
        highest_priority = person("il_pfa_highest_priority_eligible", period)
        risk_count = person("il_pfa_risk_factor_count", period)
        higher_risk = highest_priority | (risk_count >= 2)
        lower_income = person("il_pfae_income_eligible", period)
        return pfa_eligible & higher_risk & lower_income
