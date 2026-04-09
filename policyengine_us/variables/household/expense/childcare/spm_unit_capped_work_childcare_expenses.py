from policyengine_us.model_api import *


class spm_unit_capped_work_childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "SPM unit work and childcare expenses"
    definition_period = YEAR
    unit = USD

    def formula_2024(spm_unit, period, parameters):
        work_expenses = spm_unit("spm_unit_work_expenses", period)
        childcare_expenses = spm_unit(
            "spm_unit_pre_subsidy_childcare_expenses", period
        )
        earned_cap = spm_unit("spm_unit_head_spouse_earned_cap", period)
        combined_expenses = np.maximum(work_expenses + childcare_expenses, 0)
        return min_(combined_expenses, earned_cap)
