from policyengine_us.model_api import *


class va_tanf_countable_earned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF countable earned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        gross_earnings = spm_unit("va_tanf_gross_earned_income", period)
        unit_size = spm_unit("spm_unit_size", period)
        p = parameters(period).gov.states.va.dss.tanf.income.deduction.earned
        annual_flat_exclusion = p.flat[unit_size] * MONTHS_IN_YEAR
        earnings_after_flat_exclusion = max_(
            gross_earnings - annual_flat_exclusion, 0
        )
        return earnings_after_flat_exclusion * (1 - p.percentage)
