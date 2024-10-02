from policyengine_us.model_api import *


class electricity_expense(Variable):
    value_type = float
    entity = SPMUnit
    label = "Electricity expense"
    unit = USD
    definition_period = YEAR

    def formula(spm_unit, period, parameters):
        pre_subsidy_electricity_expenses = spm_unit(
            "pre_subsidy_electricity_expense", period
        )
        p = parameters(period).household.expense.utilities
        subsidies = add(spm_unit, period, p.subsidies)
        return max_(pre_subsidy_electricity_expenses - subsidies, 0)
