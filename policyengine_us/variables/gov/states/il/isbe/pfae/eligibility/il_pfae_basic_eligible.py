from policyengine_us.model_api import *


class il_pfae_basic_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Meets basic eligibility for Illinois PFAE (age and income)"
    definition_period = YEAR
    reference = (
        "https://www.isbe.net/pages/preschool-for-all.aspx",
        "https://www.isbe.net/Documents/pdg-eg-grant-enrollment-form.pdf",
    )
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        # Basic eligibility: age 3-5 and income <= 400% FPL
        age_eligible = person("il_pfae_age_eligible_child", period)
        income_eligible = person("il_isbe_income_eligible", period)
        return age_eligible & income_eligible
