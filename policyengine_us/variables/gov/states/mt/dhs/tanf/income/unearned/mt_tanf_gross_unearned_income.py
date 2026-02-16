from policyengine_us.model_api import *


class mt_tanf_gross_unearned_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "Montana Temporary Assistance for Needy Families (TANF) gross unearned income"
    unit = USD
    definition_period = MONTH
    reference = "https://dphhs.mt.gov/assets/hcsd/tanfmanual/TANF501-1Jan012018.pdf#page=1"
    defined_for = StateCode.MT

    def formula(spm_unit, period, parameters):
        gross_unearned = add(
            spm_unit, period, ["mt_tanf_gross_unearned_income_person"]
        )
        child_support_expense = add(
            spm_unit, period, ["child_support_expense"]
        )
        return max_(gross_unearned - child_support_expense, 0)
