from policyengine_us.model_api import *


class al_ccsp_weekly_copay_per_child(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Alabama CCSP weekly per-child parental fee"
    definition_period = MONTH
    defined_for = StateCode.AL
    reference = "https://dhr.alabama.gov/wp-content/uploads/2024/01/Child-Care-Fact-Sheet-2024.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhr.ccsp.copay
        monthly_income = spm_unit("al_ccsp_countable_income", period)
        monthly_fpg = spm_unit("spm_unit_fpg", period)
        fpl_ratio = where(monthly_fpg > 0, monthly_income / monthly_fpg, 0)
        fee = p.fee_by_fpl.calc(fpl_ratio)
        copay_waived = spm_unit("al_ccsp_copay_waived", period)
        return where(copay_waived, 0, fee)
