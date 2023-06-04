from policyengine_us.model_api import *


class va_tanf_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF countable income"
    unit = USD
    definition_period = YEAR
    defined_for = defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        grant_standard = spm_unit("va_tanf_grant_standard", period)
        up_grant_standard = spm_unit("va_tanf_up_grant_standard", period)
        up_tanf_eligibility = spm_unit("va_up_tanf_eligibility", period)
        grant = where(up_tanf_eligibility, up_grant_standard, grant_standard)
        countable_earned_income = spm_unit("va_tanf_countable_earned_income", period)
        care_expenses = spm_unit("va_tanf_care_expenses", period)
        countable_unearned_income = spm_unit("va_tanf_countable_unearned_income", period)
        return max_(countable_earned_income - care_expenses + countable_unearned_income, 0)