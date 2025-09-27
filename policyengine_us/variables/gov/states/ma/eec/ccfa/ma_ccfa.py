from policyengine_us.model_api import *


class ma_ccfa(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = (
        "Massachusetts Child Care Financial Assistance (CCFA) benefit amount"
    )
    definition_period = MONTH
    defined_for = "ma_ccfa_eligible"
    reference = "https://www.mass.gov/doc/fiscal-year-2025-child-care-financial-assistance-daily-reimbursement-rates/download"

    def formula(spm_unit, period, parameters):
        pre_subsidy_childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period.this_year
        )
        copay = spm_unit("ma_ccfa_total_copay", period)
        max_reimbursement = add(
            spm_unit, period, ["ma_ccfa_maximum_reimbursement"]
        )
        uncapped_benefit = max_(pre_subsidy_childcare_expenses - copay, 0)

        return min_(uncapped_benefit, max_reimbursement)
