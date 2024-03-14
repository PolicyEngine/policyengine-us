from policyengine_us.model_api import *


class spm_unit_childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "Child care expenses"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        pre_subsidy_childcare_expenses = add(
            spm_unit, period, ["pre_subsidy_childcare_expenses"]
        )
        p = parameters(period).household.expense.childcare
        subsidies = add(spm_unit, period, p.subsidies)
        return max_(pre_subsidy_childcare_expenses - subsidies, 0)
