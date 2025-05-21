from policyengine_us.model_api import *


class il_tanf_countable_earned_income_at_application(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois Temporary Assistance for Needy Families (TANF) countable earned income at application"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.155"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        countable_gross_earned_income = spm_unit(
            "il_tanf_countable_gross_earned_income", period
        )
        initial_employment_deduction = add(spm_unit, period,["il_tanf_initial_employment_deduction_person"])
        return max_(countable_gross_earned_income - initial_employment_deduction, 0)
