from policyengine_us.model_api import *


class il_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF)"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.250"
    defined_for = "il_tanf_eligible"

    def formula(spm_unit, period, parameters):
        payment_level = spm_unit(
            "il_tanf_payment_level_for_grant_calculation", period
        )
        countable_income = spm_unit(
            "il_tanf_countable_income_for_grant_calculation", period
        )
        return max_(payment_level - countable_income, 0)
