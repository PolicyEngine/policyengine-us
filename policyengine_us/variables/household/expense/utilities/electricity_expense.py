from policyengine_us.model_api import *


class electricity_expense(Variable):
    value_type = float
    entity = Household
    label = "Electricity expense"
    unit = USD
    definition_period = YEAR

    def formula(household, period, parameters):
        pre_subsidy_electricity_expenses = household(
            "pre_subsidy_electricity_expense", period
        )
        p = parameters(period).household.expense.utilities
        subsidies = add(household, period, p.subsidies)
        return max_(pre_subsidy_electricity_expenses - subsidies, 0)
