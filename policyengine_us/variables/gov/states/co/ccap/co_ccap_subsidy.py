from policyengine_us.model_api import *


class co_ccap_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Colorado Child Care Assistance Program"
    unit = USD
    definition_period = MONTH
    defined_for = "co_ccap_eligible"

    def formula(spm_unit, period, parameters):
        expenses = add(
            spm_unit,
            period,
            ["pre_subsidy_childcare_expenses", "after_school_expenses"],
        )
        parent_fee = spm_unit("co_ccap_parent_fee", period)
        return max_(expenses - parent_fee, 0)
