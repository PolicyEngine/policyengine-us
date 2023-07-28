from policyengine_us.model_api import *


class va_map_mb_qmb_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP QMB income eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.map.mb
        income = spm_unit("va_map_mb_income", period)
        monthly_income = income / MONTHS_IN_YEAR
        married = spm_unit("is_married", period)
        if married:
            p = p.income_limit_couple
        else:
            p = p.income_limit_single
        return p.cal(monthly_income) == 0
