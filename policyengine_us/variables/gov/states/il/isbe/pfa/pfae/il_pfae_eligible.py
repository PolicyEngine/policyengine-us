from policyengine_us.model_api import *


class il_pfae_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Illinois Preschool For All Expansion (PFAE)"
    definition_period = YEAR
    reference = "https://www.isbe.net/pages/preschool-for-all.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # PFAE requires PFA eligibility plus stricter income limit (200% FPL).
        pfa_eligible = person("il_pfa_eligible", period)
        pfae_income_eligible = person("il_pfae_income_eligible", period)
        return pfa_eligible & pfae_income_eligible
