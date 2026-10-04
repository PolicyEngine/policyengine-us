from policyengine_us.model_api import *


class form_4952_total_investment_interest_expense(Variable):
    value_type = float
    entity = TaxUnit
    label = "Form 4952 total investment interest expense"
    unit = USD
    definition_period = YEAR
    documentation = """
    Form 4952 line 3: "Total investment interest expense. Add lines 1 and 2."
    Line 1 is "Investment interest expense paid or accrued in 2025". Sum all
    tax-unit members' investment_interest_expense, matching the existing
    deductible_interest_expense aggregation, which includes dependents.
    Prior-year disallowed investment interest (line 2) has no model input
    and is not modeled, so line 3 equals current-year line 1.
    """
    reference = [
        "https://www.law.cornell.edu/uscode/text/26/163#d_3",
        "https://www.law.cornell.edu/uscode/text/26/163#d_2",
        "https://www.irs.gov/pub/irs-pdf/f4952.pdf",
    ]

    adds = ["investment_interest_expense"]
