from policyengine_us.model_api import *


class va_map_mb_slmb_income_eligibility(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA MAP SLMB income eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        income = spm_unit("va_map_mb_income", period)
        married = spm_unit("is_married", period)
        if married:
            p = p.income_limit_couple
        else:
            p = p.income_limit_single
        return p.cal(income) == 1
