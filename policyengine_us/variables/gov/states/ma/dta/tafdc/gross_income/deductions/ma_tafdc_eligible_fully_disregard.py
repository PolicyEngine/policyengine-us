from policyengine_us.model_api import *


class ma_tafdc_eligible_fully_disregard(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Is it eligible fully disregard for the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = "https://www.masslegalservices.org/content/74-what-6-month-100-earned-income-disregard"
    defined_for = StateCode.MA

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.dta.tafdc.gross_income.deductions.full_disregard
        gross_income = spm_unit("ma_tafdc_gross_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        return gross_income < fpg * p.income_limit
