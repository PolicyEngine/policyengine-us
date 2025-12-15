from policyengine_us.model_api import *


class il_pfa_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Illinois Preschool For All"
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Eligibility requires: age 3-5, income <= 400% FPL,
        # and either a highest priority factor OR 2+ risk factors.
        eligible_child = person("il_pfa_eligible_child", period)
        income_eligible = person("il_pfa_income_eligible", period)
        risk_eligible = person("il_pfa_risk_eligible", period)
        return eligible_child & income_eligible & risk_eligible
