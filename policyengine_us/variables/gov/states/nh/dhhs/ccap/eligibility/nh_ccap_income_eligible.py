from policyengine_us.model_api import *


class nh_ccap_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Income eligible for New Hampshire Child Care Scholarship Program"
    definition_period = MONTH
    defined_for = StateCode.NH
    reference = "https://www.law.cornell.edu/regulations/new-hampshire/N-H-Admin-Code-SS-He-C-6910.06"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nh.dhhs.ccap.income
        countable_income = spm_unit("nh_ccap_countable_income", period)
        # He-C 6910.06(b): gross income <= 85% SMI
        smi = spm_unit("hhs_smi", period)
        income_limit = smi * p.income_limit_smi_rate
        income_test = countable_income <= income_limit
        # He-C 6910.06(a)(1): TANF recipients automatically qualify
        tanf_eligible = spm_unit("is_tanf_enrolled", period)
        return income_test | tanf_eligible
