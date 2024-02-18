from policyengine_us.model_api import *


class ca_investment_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California investment interest deduction"
    unit = USD
    documentation = "https://www.ftb.ca.gov/forms/2021/2021-3526.pdf"
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Lines 2, 3, 4a, 4b, 4c, 4d, 4e, 4f, 7 not included
        investment_interest_expense = person(
            "investment_interest_expense", period
        )  # Line 1
        investment_expenses = person("investment_expense", period)  # Line 5
        net_investment_income = (
            investment_interest_expense - investment_expenses
        )  # Line 6
        investment_interest_expense_deduction = min_(
            investment_interest_expense, net_investment_income
        )  # Line 8
        form_4952_amount = tax_unit(
            "investment_income_form_4952", period
        )  # Line 9
        return np.absolute(
            form_4952_amount - investment_interest_expense_deduction
        )  # Line 10
