from policyengine_us.model_api import *


class md_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MD

    def formula(spm_unit, period, parameters):
        # Maximum TANF amount recieved
        grant_standard = spm_unit("md_tanf_maximum_benefit", period)
        # SPM unit income after continuous deduction
        income = spm_unit("md_tanf_net_countable_income", period)
        # SPM Unit childcare deductions
        childcare_deduction = spm_unit("md_tanf_childcare_deduction", period)
        return max(grant_standard - (income - childcare_deduction), 0)
