from policyengine_us.model_api import *


class va_map_mb_slmb_income_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "VA MAP SLMB income eligibility"
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.map.mb
        income = spm_unit("va_map_mb_income", period)
        monthly_income = income / MONTHS_IN_YEAR
        married = add(spm_unit, period, ["is_married"]) > 0
        return (
            where(
                married,
                p.income_limit_couple.calc(monthly_income),
                p.income_limit_single.calc(monthly_income),
            )
            == 1
        )
