from policyengine_us.model_api import *


class il_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Illinois Child Care Assistance Program (CCAP) due to income"
    definition_period = MONTH
    reference = "https://www.dhs.state.il.us/page.aspx?item=118832"
    defined_for = StateCode.IL

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dhs.ccap.income.income_limit
        countable_income = spm_unit("il_ccap_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        enrolled_in_ccap = spm_unit("il_ccap_enrolled", period)
        fpg_limit = where(
            enrolled_in_ccap,
            p.redetermination_rate,
            p.new_applicants_rate,
        )
        income_limit = fpg_limit * fpg
        return countable_income <= income_limit
