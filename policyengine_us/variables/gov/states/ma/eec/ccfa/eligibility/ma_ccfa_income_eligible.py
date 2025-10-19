from policyengine_us.model_api import *


class ma_ccfa_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for Massachusetts Child Care Financial Assistance (CCFA)"
    definition_period = MONTH
    defined_for = StateCode.MA
    reference = "https://www.mass.gov/doc/financial-assistance-policy-guide"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ma.eec.ccfa.income.smi_rate

        countable_income = spm_unit("ma_ccfa_countable_income", period)
        smi = spm_unit("hhs_smi", period)

        # Initial eligibility at 50% SMI, continued at 85% SMI
        is_enrolled = spm_unit("ma_ccfa_enrolled", period)

        smi_limit = where(
            is_enrolled,
            p.redetermination,
            p.new_applicants,
        )
        income_limit = smi * smi_limit
        return countable_income <= income_limit
