from policyengine_us.model_api import *


class interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Interest deduction"
    unit = USD
    documentation = """
    Schedule A line 10: "Add lines 8e and 9." Line 8e is mortgage interest
    and line 9 is "Investment interest. Attach Form 4952 if required."
    Replace investment interest paid in deductible_interest_expense with
    the Form 4952 line 8 deduction limited under 163(d). Retain the existing
    all-member aggregation and honor direct deductible_interest_expense
    inputs by adjusting only the separately reported investment interest.
    """
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_1",
        "https://www.irs.gov/pub/irs-prior/f1040sa--2025.pdf",
        "https://www.irs.gov/pub/irs-pdf/f4952.pdf",
    ]

    def formula(tax_unit, period, parameters):
        interest_paid = add(tax_unit, period, ["deductible_interest_expense"])
        investment_interest_paid = tax_unit(
            "form_4952_total_investment_interest_expense", period
        )
        investment_interest_allowed = tax_unit(
            "investment_interest_expense_deduction", period
        )
        return interest_paid - investment_interest_paid + investment_interest_allowed
