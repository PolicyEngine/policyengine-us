from policyengine_us.model_api import *


class investment_interest_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Investment interest expense deduction"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 8: "Investment interest expense deduction. Enter the
    smaller of line 3 or line 6." Section 163(d)(1) says the investment
    interest deduction "shall not exceed the net investment income of
    the taxpayer for the taxable year". The Form 4952 line 8 instructions
    direct individuals to Schedule A line 9. Prior-year disallowed
    investment interest (line 2) is not modeled.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_1",
        "https://www.irs.gov/pub/irs-pdf/f4952.pdf",
    ]

    def formula(tax_unit, period, parameters):
        interest = tax_unit("form_4952_total_investment_interest_expense", period)
        net_income = tax_unit("form_4952_net_investment_income", period)
        return min_(interest, net_income)
