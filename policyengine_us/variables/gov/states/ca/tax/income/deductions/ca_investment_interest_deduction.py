from policyengine_us.model_api import *


class ca_investment_interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "California investment interest deduction"
    unit = USD
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-3526.pdf"
        "https://law.justia.com/codes/california/2022/code-rtc/division-2/part-11/chapter-7/article-1/section-24344/"
    )
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        # Line 1
        investment_interest_expense = add(
            tax_unit, period, ["investment_interest_expense"]
        )
        # Line 5
        investment_expenses = add(tax_unit, period, ["investment_expenses"])
        # Line 6
        net_investment_income = (
            investment_interest_expense - investment_expenses
        )
        # Line 8
        investment_interest_expense_deduction = min_(
            investment_interest_expense, net_investment_income
        )
        # Line 9
        form_4952_amount = tax_unit("investment_income_form_4952", period)
        # Line 10
        return np.abs(form_4952_amount - investment_interest_expense_deduction)
