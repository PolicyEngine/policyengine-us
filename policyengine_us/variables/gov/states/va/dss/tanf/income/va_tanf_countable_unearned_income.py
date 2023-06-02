from policyengine_us.model_api import *


class va_tanf_countable_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF gross unearned income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.VA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.va.dss.tanf.income
        up_tanf_eligibility = spm_unit("va_up_tanf_eligibility", period)
        gross_unearned = add(spm_unit, period, p.unearned)
        child_support = add(spm_unit, period, ["child_support_received"])
        interest_income = add(spm_unit, period, ["interest_income"])
        unemployment_compensation = add(spm_unit, period, ["unemployment_compensation"])
        p = p.deduction.unearned
        child_support_disregard = p.monthly_child_support * MONTHS_IN_YEAR 
        interest_income_disregard = p.montly_interest_income * MONTHS_IN_YEAR
        gross_unearned_after_disregard =  gross_unearned - min_(child_support, child_support_disregard) - min_(interest_income, interest_income_disregard)
        return where(up_tanf_eligibility,
                     gross_unearned_after_disregard - unemployment_compensation,
                     gross_unearned_after_disregard,)

