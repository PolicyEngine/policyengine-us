from policyengine_us.model_api import *


class ca_investment_interest_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California investment interest expense deduction"
    unit = USD
    reference = "https://www.ftb.ca.gov/forms/2025/2025-3526.pdf"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # FTB 3526 line 1.
        investment_interest_expense = add(
            tax_unit, period, ["investment_interest_expense"]
        )
        # FTB 3526 line 5.
        investment_expenses = add(tax_unit, period, ["investment_expenses"])
        # Simplified FTB 3526 line 6. Carryforwards and investment income
        # elections are not separately modeled here.
        net_investment_income = max_(
            0, investment_interest_expense - investment_expenses
        )
        # FTB 3526 line 8.
        return min_(investment_interest_expense, net_investment_income)
