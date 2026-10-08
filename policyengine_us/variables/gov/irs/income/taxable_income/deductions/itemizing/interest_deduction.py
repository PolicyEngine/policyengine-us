from policyengine_us.model_api import *


class interest_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Interest deduction"
    unit = USD
    documentation = """
    Schedule A line 10: "Add lines 8e and 9." Line 8e is mortgage interest
    and line 9 is "Investment interest. Attach Form 4952 if required."
    Start from the existing aggregate of deductible_interest_expense over
    every tax unit member, remove all current-year investment interest paid,
    and add the Form 4952 line 8 deduction limited under 163(d). The aggregate
    contains only current-year interest, so the prior-year carryover on Form
    4952 line 2 enters only through line 8. A dependent's investment interest
    leaves the aggregate and stays off the filer's Form 4952. Direct
    deductible_interest_expense inputs and mortgage interest keep the
    existing aggregation.
    """
    definition_period = YEAR
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_1",
        "https://www.irs.gov/pub/irs-prior/f1040sa--2025.pdf",
        "https://www.irs.gov/pub/irs-prior/f4952--2025.pdf",
    ]

    def formula(tax_unit, period, parameters):
        interest_paid = add(tax_unit, period, ["deductible_interest_expense"])
        investment_interest_paid = add(
            tax_unit, period, ["investment_interest_expense"]
        )
        investment_interest_allowed = tax_unit(
            "investment_interest_expense_deduction", period
        )
        return interest_paid - investment_interest_paid + investment_interest_allowed
