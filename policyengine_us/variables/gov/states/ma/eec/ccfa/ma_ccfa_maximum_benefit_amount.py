from policyengine_us.model_api import *


class ma_ccfa_maximum_benefit_amount(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Massachusetts Child Care Financial Assistance (CCFA) maximum benefit amount"
    definition_period = MONTH
    defined_for = "ma_ccfa_eligible"
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"

    def formula(spm_unit, period, parameters):
        copay = spm_unit("ma_ccfa_total_copay", period)
        max_reimbursement = add(
            spm_unit, period, ["ma_ccfa_maximum_reimbursement"]
        )

        return max_(max_reimbursement - copay, 0)
