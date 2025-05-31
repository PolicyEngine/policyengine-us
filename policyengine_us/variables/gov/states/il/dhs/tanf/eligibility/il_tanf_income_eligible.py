from policyengine_us.model_api import *


class il_tanf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Illinois Temporary Assistance for Needy Families (TANF) due to income"
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.155"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        countable_income = spm_unit(
            "il_tanf_countable_income_for_initial_eligibility", period
        )
        payment_level = spm_unit(
            "il_tanf_payment_level_for_initial_eligibility", period
        )
        return countable_income <= payment_level
