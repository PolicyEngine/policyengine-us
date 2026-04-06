from policyengine_us.model_api import *


class il_pi_basic_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets basic eligibility for Illinois PI (age and income)"
    definition_period = YEAR
    reference = "https://www.isbe.net/Pages/Birth-to-Age-3-Years.aspx"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Basic eligibility: demographic eligible (child under 3 or pregnant)
        # and income eligible (≤400% FPL).
        demographic_eligible = person("il_pi_demographic_eligible", period)
        income_eligible = person("il_isbe_income_eligible", period)
        return demographic_eligible & income_eligible
