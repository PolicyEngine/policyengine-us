from policyengine_us.model_api import *


class childcare_expenses(Variable):
    value_type = float
    entity = SPMUnit
    label = "Child care expenses"
    definition_period = YEAR
    unit = USD

    def formula(spm_unit, period, parameters):
        pre_subsidy = add(spm_unit, period, ["pre_subsidy_childcare_expenses"])
        p = parameters(period).gov.household.expense.childcare
        subsidies = add(spm_unit, period, p.subsidy_programs)
        return max_(pre_subsidy - subsidies, 0)
